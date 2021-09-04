# bot.py
"""Main bot file that instances and runs the bot and loads the extensions"""

from datetime import datetime, timedelta

import discord
from discord.ext import commands

import database
from resources import settings

intents = discord.Intents.none()
intents.guilds = True   # for on_guild_join() and bot.guilds
intents.messages = True   # for literally everything the bot does


bot = commands.Bot(command_prefix=database.get_prefix_all, help_command=None, case_insensitive=True, intents=intents)


EXTENSIONS = [
    'cogs.auto_flex',
    'cogs.dev',
    'cogs.events',
    'cogs.main',
    'cogs.settings'
]
if __name__ == '__main__':
    for extension in EXTENSIONS:
        bot.load_extension(extension)


bot.run(settings.TOKEN)