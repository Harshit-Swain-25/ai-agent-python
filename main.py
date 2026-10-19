
import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors

MODEL_NAME = "gemini-3.8-flash"

AGENT_INSTRUCTIONS = (
    "You are a helpful learning Python Assistant. "
    "Explain concepts in simple language and use concise answers. "
    "Be honest when you are unsure."
)

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
            "a": {"type": "number", "description": "The first number."},
            "b": {"type": "number", "description": "The second number."},
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
                "description": "The arithmetic operation to perform.",
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


class Agent:
    def __init__(self, client, model_name, instructions):
        self.client = client
        self.model_name = model_name
        self.instructions = instructions
        self.history = []
        self.previous_interaction_id = None

    def ask(self, question):
        request_options = {
            "model": self.model_name,
            "input": (
                f"Instructions for the assistant: {self.instructions}\n\n"
                f"User question: {question}"
            ),
            "tools": [CALCULATOR_TOOL],
        }

        if self.previous_interaction_id is not None:
            request_options["previous_interaction_id"] = (
                self.previous_interaction_id
            )

        interaction = self.client.interactions.create(**request_options)

        function_call = next(
            (
                step
                for step in interaction.steps
                if step.type == "function_call"
            ),
            None,
        )

        if function_call is not None:
            result = execute_tool(
                function_call.name,
                function_call.arguments,
            )

            print(f"Tool used: {function_call.name}")
            print(f"Tool result: {result}")

            interaction = self.client.interactions.create(
                model=self.model_name,
                previous_interaction_id=interaction.id,
                input=[
                    {
                        "type": "function_result",
                        "name": function_call.name,
                        "call_id": function_call.id,
                        "result": [
                            {"type": "text", "text": str(result)}
                        ],
                    }
                ],
            )

        answer = interaction.output_text

        if not answer:
            raise RuntimeError("The agent did not return a text answer.")

        self.history.append({"role": "user", "content": question})
        self.history.append({"role": "assistant", "content": answer})
        self.previous_interaction_id = interaction.id

        return answer


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Error: GEMINI_API_KEY is missing from your .env file.")
        return

    try:
        client = genai.Client(api_key=api_key)

        agent = Agent(
            client=client,
            model_name=MODEL_NAME,
            instructions=AGENT_INSTRUCTIONS,
        )

        print("AI Learning Agent")
        print("Type 'exit' to quit.\n")

        while True:
            question = input("You: ").strip()
            if question.lower() == "exit":
                print("Goodbye!")
                break
            
            if not question:
                print("Please enter a question.\n")
                continue

            try:
                answer = agent.ask(question)
                print(f"\nAgent: {answer}")
                print(f"Messages recorded: {len(agent.history)}\n")
            except errors.APIError as error:
                print(f"Gemini request failed: {type(error).__name__}")
                print("Check your API key, model access, and quota.\n")
            except (TimeoutError, ConnectionError) as error:
                print(f"Network request failed: {type(error).__name__}")
                print("Check your internet connection and try again.\n")
            except (ValueError, TypeError, RuntimeError) as error:
                print(f"Agent execution failed: {error}\n")


    except errors.APIError as error:
        print(f"Gemini request failed: {type(error).__name__}")
        print("Check your API key, model access, and quota.")

    except (TimeoutError, ConnectionError) as error:
        print(f"Network request failed: {type(error).__name__}")
        print("Check your internet connection and try again.")

    except (ValueError, TypeError, RuntimeError) as error:
        print(f"Agent execution failed: {error}")


if __name__ == "__main__":
    main()
