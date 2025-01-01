import time
import prompt_manager

manager = prompt_manager.PromptManager("prompts")

while True:
    print(manager.list_prompts())
    time.sleep(5)