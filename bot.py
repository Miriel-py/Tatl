# bot.py
"""Main bot file that instances and runs the bot and loads the extensions"""

import discord
from discord.ext import commands

from resources import settings

intents = discord.Intents.none()
intents.guilds = True   # for on_guild_join() and all guild objects
intents.messages = True   # for literally everything the bot does


if settings.DEBUG_MODE == 'ON':
    bot = commands.Bot(help_command=None, case_insensitive=True, intents=intents,
                       debug_guilds=settings.DEV_GUILDS, owner_id=619879176316649482)
else:
    bot = commands.Bot(help_command=None, case_insensitive=True, intents=intents,
                       owner_id=619879176316649482)


EXTENSIONS = [
    'cogs.auto_flex',
    'cogs.dev',
    'cogs.events',
    'cogs.main',
    'cogs.settings',
    'cogs.virtual_fisher'
]
if __name__ == '__main__':
    for extension in EXTENSIONS:
        bot.load_extension(extension)


bot.run(settings.TOKEN)