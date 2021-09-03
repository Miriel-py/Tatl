# dev.py
"""Contains internal dev commands"""

import asyncio
import importlib
import sys

import discord
from discord.ext import commands

import database
from resources import emojis, strings


class DevCog(commands.Cog):
    """Cog with internal dev commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands
    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def dev(self, ctx: commands.Context, *args: str) -> None:
        """Dev command group, lists all dev commands"""
        subcommands = ''
        for command in self.bot.walk_commands():
            if isinstance(command, commands.Group):
                if command.qualified_name == 'dev':
                    for subcommand in command.walk_commands():
                        if subcommand.parents[0] == command:
                            aliases = f'`{subcommand.qualified_name}`'
                            for alias in subcommand.aliases:
                                aliases = f'{aliases}, `{alias}`'
                            subcommands = f'{subcommands}{emojis.BP} {aliases}\n'
        await ctx.reply(
            f'Available dev commands:\n'
            f'{subcommands}',
            mention_author=False
        )

    @dev.command()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def reload(self, ctx: commands.Context, mod_or_cog: str, *args: str) -> None:
        """Reloads modules and cogs"""
        message_syntax = strings.MSG_SYNTAX.format(syntax=f'{ctx.prefix}dev reload [mod|cog] [name(s)]')
        if not args:
            await ctx.send(message_syntax)
            return
        actions = []
        if mod_or_cog in ('lib','libs','modules','module','mod','mods'):
            for module_name in args:
                try:
                    module = sys.modules.get(module_name)
                    if module is not None:
                        importlib.reload(module)
                        actions.append(f'➜ Module \'{module_name}\' reloaded.')
                    else:
                        actions.append(f'➜ **Module \'{module_name}\' not found.**')
                except Exception as error:
                    await ctx.send(error)
                    return
        elif mod_or_cog in ('cog','cogs','extension','ext','extensions'):
            cog_names = [f'cogs.{arg}' for arg in args]
            for cog_name in cog_names:
                try:
                    cog_reload_status = self.bot.reload_extension(cog_name)
                except:
                    actions.append(f'➜ **Extension \'{cog_name}\' not found.**')
                else:
                    if cog_reload_status is None:
                        actions.append(f'➜ Extension \'{cog_name}\' reloaded.')
                    else:
                        actions.append(f'{cog_reload_status}')
        else:
            await ctx.send(message_syntax)
            return
        message = ''
        for action in actions:
            message = f'{message}\n{action}'
        await ctx.send(message)

    @dev.command()
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True)
    async def shutdown(self, ctx: commands.Context) -> None:
        """Shuts down the bot"""
        def check(message):
            return (message.author == ctx.author) and (message.channel == ctx.channel)

        user_name = ctx.author.name
        await ctx.reply(f'**{user_name}**, are you **SURE**?', mention_author=False)
        try:
            answer = await self.bot.wait_for('message', check=check, timeout=30)
            if answer.content.lower() in ('yes','y'):
                await ctx.send('Shutting down.')
                await self.bot.close()
            else:
                await ctx.send('Shutdown aborted. Phew.')
        except asyncio.TimeoutError as error:
            await ctx.send('Oh good, he forgot to answer.')


# Initialization
def setup(bot):
    bot.add_cog(DevCog(bot))