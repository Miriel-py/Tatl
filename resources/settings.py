# settings.py

import os

from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEBUG_MODE = os.getenv('DEBUG_MODE')

BOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BOT_DIR, 'database/tatl_db.db')
LOG_FILE = os.path.join(BOT_DIR, 'logs/discord.log')

OWNER_ID = 619879176316649482
DEV_GUILDS = [730115558766411857,]

EPIC_RPG_ID = 555955826880413696
RUMBLE_ROYALE_ID = 693167035068317736
VIRTUAL_FISHER_ID = 574652751745777665

# Embed color
EMBED_COLOR = 0xFFE600

# Set default footer
DEFAULT_FOOTER = 'Ding ding ding!'