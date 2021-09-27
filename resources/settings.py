# settings.py

import os

from dotenv import load_dotenv


# Read the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEBUG_MODE = os.getenv('DEBUG_MODE')

BOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BOT_DIR, 'database/tatl_db.db')
LOG_FILE = os.path.join(BOT_DIR, 'logs/discord.log')

DONOR_COOLDOWNS = (1, 0.9, 0.8, 0.65,)

DEFAULT_PREFIX = 'tatl '

EPIC_RPG_ID = 555955826880413696
RUMBLE_ROYALE_ID = 693167035068317736

# Embed color
EMBED_COLOR = 0xFFE600

# Set default footer
FOOTER = 'Ding ding ding!'

# Error log file
