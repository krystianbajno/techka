from datetime import date
import random
from core.cli.colors import *

from core.cli.images import IMAGES
from core.cli.texts import TEXTS

def logo():
    current_date = date.today()
    
    colors = [
        RED,
        GREEN,
        ""
    ]
    
    choice_img = random.choice(IMAGES)
    choice_color = random.choice(colors)
    choice_text = random.choice(TEXTS)
    
    return f"""
{RED}{BOLD}T E C H K A{RESET} v4.20.69 - {BOLD}{current_date.year}{RESET}

{choice_color}{choice_img}{RESET}
{choice_text}

{RED}{BOLD}T E C H K A{RESET} v4.20.69 - {BOLD}{current_date.year}{RESET}

{BOLD}{GREEN}https://github.com/krystianbajno/techka{RESET}
"""


