import json
import subprocess
from os import getenv
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv
from groq import Groq

from Integrations.Pandas.Service.pandas_service import PandasService


class GroqService:
    """
    Manages interactions with Groq AI for spreadsheet analysis.

    Responsibilities:
    - Initialize the Groq client.
    - Manage conversation history.
    - Register tools and make them available through function calling.
    - Process tool calls requested by the AI.
    - Generate, save, and execute Python scripts.
    """

    MAX_TOOL_ITERATIONS = 10

    def __init__(
        self,
        spreadsheet_columns: list[str],
        spreadsheet_path: Path,
    ) -> None:
        load_dotenv()

        api_key = getenv("GROQ_API_KEY")
        self.model = getenv("GROQ_MODEL")

        if not api_key:
            raise ValueError("GROQ_API_KEY has not been configured.")

        if not self.model:
            raise ValueError("GROQ_MODEL has not been configured.")

        self.client = Groq(api_key=api_key)
        self.spreadsheet_columns = spreadsheet_columns
        self.spreadsheet_path = spreadsheet_path
        self.output_path = Path(__file__).resolve().parent.parent / "groq_working.py"

        self.tools: dict[str, dict[str, Any]] = {}
        self.messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": self.get_system_prompt(),
            }
        ]

        self.pandas_service = PandasService(spreadsheet_path)
        self.register_tools()

    def get_system_prompt(self) -> str:
        return f"""
You are an assistant specialized in spreadsheet analysis using Python and Pandas.

Available columns:
{self.spreadsheet_columns}

Priority rules:
{getenv("SYSTEM_CONTENT", "")}

Rules:
- Use Python and Pandas to work with the spreadsheet.
- Never invent column names.
- Assume the spreadsheet must be loaded into a DataFrame named df.
- When the user requests code, generate a complete Python script.
- When generating a script, use the write_code_to_file tool to save it.
- The output file must be named groq_working.py.
- Never claim that code was executed if it was only saved.
- Keep your answers objective.
- Do not write comments in generated code.
- Three spreadsheet-reading tools are available. Use read_all_rows only as a last resort, when it is the only way to answer the user.
- The generated script must include this structure:
    from os import getenv
    from dotenv import load_dotenv
    from pathlib import Path

    load_dotenv(override=True)

    class GroqWorking:
        @staticmethod
        def main():
            spreadsheet_path = (
                Path(__file__).resolve().parent.parent.parent
                / "Working_spreadsheet"
                / getenv("WORKING_SPREADSHEET_NAME")
            )

    if __name__ == "__main__":
        GroqWorking.main()
- You may complete or modify the structure above, but you must not remove any of its elements.
- After generating the code, execute it using the execute_script_in_docker tool and show the result to the user.
- The spreadsheet_path variable may only receive the path expression defined above.
"""

    def register_tool_structure(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable[..., Any],
    ) -> None:
        if name in self.tools:
            raise ValueError(f"The tool '{name}' has already been registered.")

        definition = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        }

        self.tools[name] = {
            "definition": definition,
            "handler": handler,
        }

    def get_tools(self) -> list[dict[str, Any]]:
        return [
            tool["definition"]
            for tool in self.tools.values()
        ]

    def register_tools(self) -> None:
        self.register_tool_structure(
            name="write_code_to_file",
            description="Saves Python code to a file.",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to save.",
                    },
                },
                "required": ["code"],
                "additionalProperties": False,
            },
            handler=self.write_code_to_file,
        )

        self.register_tool_structure(
            name="read_first_rows",
            description="Reads the first 10 spreadsheet rows and returns them as a Python list.",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            handler=self.read_first_rows,
        )

        self.register_tool_structure(
            name="read_all_rows",
            description="Reads all spreadsheet rows and returns them as a Python list.",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            handler=self.read_all_rows,
        )

        self.register_tool_structure(
            name="execute_script_in_docker",
            description="Executes the AI-generated Python script inside the Docker container.",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            handler=self.execute_script_in_docker,
        )

    def execute_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> str:
        tool = self.tools.get(name)

        if tool is None:
            return json.dumps({
                "success": False,
                "error": f"Tool '{name}' was not found.",
            })

        try:
            result = tool["handler"](**arguments)
            return json.dumps(
                {
                    "success": True,
                    "result": result,
                },
                ensure_ascii=False,
                default=str,
            )
        except Exception as exception:
            return json.dumps(
                {
                    "success": False,
                    "error": str(exception),
                },
                ensure_ascii=False,
            )

    def write_code_to_file(self, code: str) -> str:
        self.output_path.write_text(code, encoding="utf-8")
        return f"File saved to {self.output_path}"

    def do_call(self, user_input: str) -> str:
        self.messages.append({
            "role": "user",
            "content": user_input,
        })

        for _ in range(self.MAX_TOOL_ITERATIONS):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.get_tools(),
                tool_choice="auto",
                temperature=0.1,
            )

            message = response.choices[0].message
            tool_calls = message.tool_calls

            if not tool_calls:
                content = message.content or ""
                self.messages.append({
                    "role": "assistant",
                    "content": content,
                })
                return content

            self.messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    tool_call.model_dump(exclude_none=True)
                    for tool_call in tool_calls
                ],
            })

            for tool_call in tool_calls:
                function_name = tool_call.function.name

                try:
                    arguments = json.loads(tool_call.function.arguments)

                    if not isinstance(arguments, dict):
                        raise ValueError("Tool arguments must be a JSON object.")

                    result = self.execute_tool(
                        name=function_name,
                        arguments=arguments,
                    )
                except (json.JSONDecodeError, ValueError) as exception:
                    result = json.dumps({
                        "success": False,
                        "error": str(exception),
                    }, ensure_ascii=False)

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        raise RuntimeError("The AI exceeded the maximum number of tool iterations.")

    def read_first_rows(self) -> list[list[Any]]:
        return self.pandas_service.read_first_rows()

    def read_all_rows(self) -> list[list[Any]]:
        return self.pandas_service.read_all_rows()

    def execute_script_in_docker(self) -> str:
        try:
            result = subprocess.run(
                ["docker", "compose", "run", "--build", "--rm", "python-app"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as exception:
            raise RuntimeError(
                f"Error while executing the generated Python script: {exception.stderr}"
            ) from exception
