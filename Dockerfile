FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1

COPY requeriments.txt .

RUN pip install --no-cache-dir -r requeriments.txt

COPY . . 

CMD ["python", "/app/Integrations/Groq/groq_working.py"]