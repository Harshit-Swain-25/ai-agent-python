import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import Mock

from main import Agent, calculator, execute_tool


class TestCalculator(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(calculator(10, 5, "add"), 15)

    def test_subtraction(self):
        self.assertEqual(calculator(10, 5, "subtract"), 5)

    def test_multiplication(self):
        self.assertEqual(calculator(20, 8, "multiply"), 160)

    def test_division(self):
        self.assertEqual(calculator(10, 5, "divide"), 2)

    def test_division_by_zero(self):
        with self.assertRaises(ValueError):
            calculator(10, 0, "divide")

    def test_unsupported_operation(self):
        with self.assertRaises(ValueError):
            calculator(10, 5, "power")

    def test_invalid_number(self):
        with self.assertRaises(TypeError):
            calculator("10", 5, "add")


class TestToolExecution(unittest.TestCase):
    def test_execute_calculator(self):
        result = execute_tool(
            "calculator",
            {"a": 20, "b": 8, "operation": "multiply"},
        )
        self.assertEqual(result, 160)

    def test_unknown_tool(self):
        with self.assertRaises(ValueError):
            execute_tool("unknown_tool", {})

    def test_missing_arguments(self):
        with self.assertRaises(ValueError):
            execute_tool(
                "calculator",
                {"a": 20, "operation": "multiply"},
            )

    
    def test_arguments_must_be_a_dictionary(self):
        with self.assertRaises(TypeError):
            execute_tool("calculator", "not a dictionary")

    def test_extra_arguments_are_rejected(self):
        with self.assertRaises(ValueError):
            execute_tool(
                "calculator",
                {
                    "a": 20,
                    "b": 8,
                    "operation": "multiply",
                    "extra": 123,
                },
            )

    def test_boolean_is_not_a_valid_number(self):
        with self.assertRaises(TypeError):
            execute_tool(
                "calculator",
                {"a": True, "b": 8, "operation": "multiply"},
            )

class TestAgent(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.agent = Agent(
            client=self.client,
            model_name="test-model",
            instructions="Be helpful.",
        )

    def test_returns_normal_text_answer(self):
        response = SimpleNamespace(
            id="interaction-1",
            steps=[],
            output_text="An AI agent can use tools.",
        )
        self.client.interactions.create.return_value = response

        answer = self.agent.ask("What is an AI agent?")

        self.assertEqual(answer, "An AI agent can use tools.")
        self.assertEqual(len(self.agent.history), 2)
        self.assertEqual(
            self.agent.previous_interaction_id,
            "interaction-1",
        )

    def test_executes_tool_and_returns_final_answer(self):
        first_response = SimpleNamespace(
            id="interaction-1",
            steps=[
                SimpleNamespace(
                    type="function_call",
                    id="call-1",
                    name="calculator",
                    arguments={
                        "a": 20,
                        "b": 8,
                        "operation": "multiply",
                    },
                )
            ],
            output_text="",
        )

        final_response = SimpleNamespace(
            id="interaction-2",
            steps=[],
            output_text="20 multiplied by 8 is 160.",
        )

        self.client.interactions.create.side_effect = [
            first_response,
            final_response,
        ]

        with redirect_stdout(StringIO()):
            answer = self.agent.ask("Multiply 20 by 8.")

        self.assertEqual(answer, "20 multiplied by 8 is 160.")
        self.assertEqual(
            self.client.interactions.create.call_count,
            2,
        )
        self.assertEqual(
            self.agent.previous_interaction_id,
            "interaction-2",
        )
        self.assertEqual(len(self.agent.history), 2)

    def test_rejects_empty_answer(self):
        response = SimpleNamespace(
            id="interaction-1",
            steps=[],
            output_text="",
        )
        self.client.interactions.create.return_value = response

        with self.assertRaises(RuntimeError):
            self.agent.ask("Hello")



if __name__ == "__main__":
    unittest.main()
