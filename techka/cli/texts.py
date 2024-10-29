import os
UPPERCASE_USERNAME = lambda: os.environ.get('USER', os.environ.get("USERNAME")).capitalize()
TEXTS = [
    f"Who are we looking for today, {UPPERCASE_USERNAME()}?",
    f"It's not about changing the world. It's about leaving the world the way it is.",
    f".45 huh? Incredible.",
    "Prepare intensely. Study the problem. Learn everything you can. Analyze all approaches. Perfect execution.",
    f"Trust is hard to come by in this line of work, {UPPERCASE_USERNAME()}.",
    "The world doesn't need heroes. It needs professionals.",
    f"Sometimes, {UPPERCASE_USERNAME()}, the best disguise is no disguise at all.",
    "There's always a plan B, but you only get one shot at plan A.",
    "Silent footsteps, clear mind. Let's keep it professional.",
    f"Think twice, act once, {UPPERCASE_USERNAME()}.",
    "In the shadows, every movement counts.",
    "The game is always played in silence.",
    "Intelligence is a weapon. Strategy is the battlefield.",
    "Luck favors the prepared, but this isn't about luck.",
    f"Stay sharp, {UPPERCASE_USERNAME()}. Everyone has a role to play.",
    f"Welcome back, {UPPERCASE_USERNAME()}. Let's make this count.",
]