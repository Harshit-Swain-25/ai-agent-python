
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

MODEL_NAME = "gemini-3.8-flash"

CALCULATOR_TOOL = {
    "type": "function",
    "name": "calculator",
    "description": (
        "Perform basic arithmetic using two numbers. "
        "Supported operations are add, subtract, multiply, and divide."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"},
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
            },
        },
        "required": ["a", "b", "operation"],
    },
}


def calculator(a, b, operation):
   if (
    isinstance(a, bool)
    or not isinstance(a, (int, float))
    or isinstance(b, bool)
    or not isinstance(b, (int, float))
   ):
    raise TypeError("Both arguments must be numbers.")
   
   if operation == "add":
        return a + b
   
   if operation == "subtract":
        return a - b
   
   if operation == "multiply":
        return a * b
   
   if operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b
   raise ValueError("Unsupported operation.")


def execute_tool(function_name, arguments):
    if function_name != "calculator":
        raise ValueError("Unsupported tool requested.")

    if not isinstance(arguments, dict):
        raise TypeError("Tool arguments must be a dictionary.")

    if set(arguments) != {"a", "b", "operation"}:
        raise ValueError("Missing or unexpected tool arguments.")

    return calculator(
        a=arguments["a"],
        b=arguments["b"],
        operation=arguments["operation"],
    )


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY is missing.")
        return

    client = genai.Client(api_key=api_key)

    try:
        response = client.interactions.create(
            model=MODEL_NAME,
            input="Use the calculator to calculate 125 multiplied by 8.",
            tools=[CALCULATOR_TOOL],
            generation_config={
                "tool_choice": {
                    "allowed_tools": {
                        "mode": "any",
                        "tools": ["calculator"],
                    }
                }
            },
        )

        for step in response.steps:
            if step.type != "function_call":
                continue

        print("Function requested:", step.name)
        print("Arguments received:", step.arguments)

        result = execute_tool(step.name, step.arguments)
        print("Calculator result:", result)

        final_interaction = client.interactions.create(
            model=MODEL_NAME,
            previous_interaction_id=response.id,
            tools=[CALCULATOR_TOOL],
            input=[
                {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [
                        {"type": "text", "text": str(result)}
                    ],
                }
            ],
        )

        print("Gemini's final answer:")
        print(final_interaction.output_text)

    except (ValueError, TypeError) as error:
        print(f"Tool execution failed: {error}")

    except errors.APIError as error:
        print(f"Gemini API request failed: {type(error).__name__}")
        print("Check your API key, model access, and quota.")

    except (TimeoutError, ConnectionError) as error:
        print(f"Network request failed: {type(error).__name__}")
        print("Check your internet connection and try again.")


if __name__ == "__main__":
    main()
