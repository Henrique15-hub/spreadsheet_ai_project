# This is a system that uses AI (Groq) and Pandas to get any information or forecast that user asked

# In this system is possible to talk with AI about the spreadsheet, asking for informations, forecasts, ways to get any wanted information and any other thing about the spreadsheet that user wants.

# All private information is on .env, AI didn't recive any private/sensitive information.
## All AI code runs into an dokcer container with some security precautions listed below:
### - No internet conection
### - Ram memory only 1GB
### - Cpu only 1 core
### - Not using root user
### - User without any linux privileges
### - All passed files with read-only property
### - Docker script only runs once per call
### - Remove contatiner after finish running (--rm)

# Used technologies:
## Python, Docker

# Used python libraries:
## os, json, typing

# Used external python libraries:
## Groq, pathlib, dotenv, subprocess, pandas

# How the system's cycle works:
## The user ask something to the AI, the AI determines whether it needs to invoke any of the function defined in the system (by `register_tool()`). If necessary, it performs a "function call", writes a Python Code (with Pandas library) into a file named 'groq_working.py', executes that code in docker using one of it tools (`execute_script_in_docker`)`, then give the anser for user's question

# System limitations:
## At the moment, the system only works with spreadsheets

## User have to format the spreadsheet to work (see more in 'How to use')

# How to use:

## Clone this repository

## Install all dependencies (if you don't have):
`pip install pathlib Groq dotenv pandas openpyxl xlrd pyxlsb pathlib`

## Create .env and copy .env.example to it

## Add your 'GROQ_API_KEY' (you can get in website: `https://groq.com`)

## Format the choosed spreadsheet by deleting all empty espaces above the columns, change the column's name for an descriptive name (money => salary) for better responses.

## Put the choosed spreadsheet in 'Working_spreadsheet'

## Change the spreadsheet's name in 'WORKING_SPREADSHEET_NAME' in .env file

## Start the system with the command: `python3 -u "you path to Main.py here"`

## Ask AI anything about the spreadsheet!