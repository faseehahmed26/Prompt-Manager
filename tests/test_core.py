import unittest
from prompt_manager.core import PromptManager


class TestPromptManager(unittest.TestCase):
    def test_add_and_get_prompt(self):
        manager = PromptManager("test_prompts")
        manager.add_prompt_version(
            "welcome", "1.0.0", "Hello, {name}!", ["name"], "Welcome message."
        )
        result = manager.get_prompt("welcome", {"name": "Alice"})
        self.assertEqual(result, "Hello, Alice!")
