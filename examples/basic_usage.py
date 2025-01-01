import os

# os.chdir("../")
print(os.getcwd())
from prompt_manager.core import PromptManager

manager = PromptManager("prompts")
manager.add_prompt_version(
    "greeting", "1.0.0", "Hello, {name}!", ["name"], "A simple greeting."
)
print(manager.get_prompt("greeting", {"name": "Alice"}))
