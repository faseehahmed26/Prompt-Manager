import prompt_manager

manager = prompt_manager.PromptManager("prompts")

# Adding version 1.0.0 of the prompt
manager.add_prompt_version(
    "welcome_message",
    "1.0.0",
    "Hello, {name}! Welcome to our platform.",
    ["name"],
    "Basic welcome message"
)

# Adding version 1.1.0 of the prompt
manager.add_prompt_version(
    "welcome_message",
    "1.1.0",
    "Hi, {name}! We're glad you're here. Start exploring {platform}!",
    ["name", "platform"],
    "Enhanced welcome message"
)

# Fetching the latest version (default behavior)
print(manager.get_prompt("welcome_message", {"name": "Alice", "platform": "PromptManager"}))

# Fetching a specific version
print(manager.get_prompt("welcome_message", {"name": "Alice"}, version="1.0.0"))


print("Available Prompts:")
for prompt in manager.list_prompts():
    print(f"Name: {prompt['name']}")
    print(f"Current Version: {prompt['current_version']}")
    print(f"Versions: {', '.join(prompt['versions'])}")
    print()


try:
    manager.add_prompt_version(
        "farewell",
        "1.0.0",
        "Goodbye, {name}! Hope to see you again.",
        ["name"],
        "Farewell message"
    )
    # Attempt to fetch the prompt without providing the required variable
    print(manager.get_prompt("farewell", {}))
except ValueError as e:
    print(f"Error: {e}")
