import os
UPPERCASE_USERNAME = lambda: os.environ.get('USER', os.environ.get("USERNAME")).capitalize()
TEXTS = [
    f"Who are we looking for today, {UPPERCASE_USERNAME()}?",
    f"It’s not about changing the world. It’s about leaving the world the way it is.",
    f".45 huh? Incredible."
]