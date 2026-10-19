# AI Learning Agent

A Python AI agent powered by Google's Gemini API. It answers questions, calls a Python calculator tool when appropriate, and uses the tool result to generate a final response.

## Features

- Gemini API integration using the `google-genai` SDK
- Interactive command-line interface
- Calculator tool for addition, subtraction, multiplication, and division
- Input validation and error handling
- Conversation continuity across questions
- Automated tests using Python's built-in `unittest`
- Code-quality checks using Ruff

## Tech Stack

- Python
- Google Gemini API
- google-genai
- python-dotenv
- unittest
- Ruff

## Prerequisites

- Python 3.10 or newer
- A Gemini API key with access to the configured model
- Internet connection

## Setup

### 1. Create a virtual environment

On macOS or Linux:

    python3 -m venv .venv
    source .venv/bin/activate

### 2. Install dependencies

    pip install -r requirements.txt

### 3. Configure your API key

Copy the example environment file:

    cp .env.example .env

Edit `.env` and replace the placeholder with your own Gemini API key:

    GEMINI_API_KEY=your_gemini_api_key_here

Never commit your real API key to Git.

## Run the agent

    python main.py

Enter questions at the prompt. Type `exit` to quit.

Example:

    You: Multiply 20 by 8
    Tool used: calculator
    Tool result: 160

The agent then uses the result to generate a final answer. Exact responses may vary.

## Run automated tests

    python -m unittest -v

The tests cover calculator operations, invalid inputs, tool dispatch, and simulated agent responses without making real Gemini API calls.

## Check code quality

    ruff check .

## Project structure

    ai-agent-python/
    ├── main.py
    ├── test_main.py
    ├── test_tool_call.py
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    └── README.md

## Current limitations

- The calculator is the currently implemented tool.
- Tool execution is restricted to explicitly supported functions.
- Unit tests use simulated Gemini responses; they do not replace live API testing.
- Model availability, API quotas, and pricing depend on Google's current policies and your account.

## Learning outcomes

This project demonstrates Python application structure, API integration, function calling, input validation, automated testing, and Git version control.
