import os
UPPERCASE_USERNAME = lambda: os.environ.get('USER', os.environ.get("USERNAME")).capitalize()
TEXTS = [
    f"😈 Who are we looking for today, {UPPERCASE_USERNAME()}?",
    f".45 huh? Incredible.",
    "Prepare intensely. Study the problem. Learn everything you can. Analyze all approaches. Perfect execution.",
    f"Trust is hard to come by in this line of work, {UPPERCASE_USERNAME()}.",
    f"Sometimes, {UPPERCASE_USERNAME()}, the best disguise is no disguise at all.",
    "There's always a plan B, but you only get one shot at plan A.",
    "Reminder - this game is played in silence.",
    "Luck favors the prepared, but this isn't about luck.",
    f"Welcome back, {UPPERCASE_USERNAME()}. Let's make this count."
]