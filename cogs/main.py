# main.py
"""Contains error handling and the help and about commands"""

from datetime import datetime

import discord
from discord.commands.commands import slash_command
from discord.ext import commands, tasks

import database
from resources import emojis, exceptions, logs, settings


class MainCog(commands.Cog):
    """Cog with events and help and about commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands
    @slash_command(name='help')
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def main_help(self, ctx: commands.Context) -> None:
        """Main help command"""
        embed = await embed_main_help(ctx)
        await ctx.respond(embed=embed)

    @slash_command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def about(self, ctx: commands.Context):
        """Shows some info about Tatl"""
        start_time = datetime.utcnow()
        await ctx.respond('Testing API latency...')
        message = await ctx.interaction.original_message()
        end_time = datetime.utcnow()
        api_latency = end_time - start_time
        embed = await embed_about(self.bot, ctx, api_latency)
        await message.edit(content=None, embed=embed)

     # Events
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Runs when an error occurs and handles them accordingly.
        Interesting errors get written to the database for further review.
        """
        async def send_error() -> None:
            """Sends error message as embed"""
            embed = discord.Embed(title='An error occured')
            embed.add_field(name='Command', value=f'`{ctx.command.name}`', inline=False)
            embed.add_field(name='Error', value=f'```py\n{error}\n```', inline=False)
            await ctx.respond(embed=embed)

        if isinstance(error, (commands.CommandNotFound, commands.NotOwner)):
            return
        elif isinstance(error, commands.DisabledCommand):
            await ctx.respond(f'Command `{ctx.command.qualified_name}` is temporarily disabled.')
        elif isinstance(error, (commands.MissingPermissions, commands.MissingRequiredArgument,
                                commands.TooManyArguments, commands.BadArgument)):
            await send_error()
        elif isinstance(error, commands.BotMissingPermissions):
            if 'send_messages' in error.missing_perms:
                return
            if 'embed_links' in error.missing_perms:
                await ctx.respond(error)
            else:
                await send_error()
        else:
            await database.log_error(error, ctx)
            await send_error()


    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Fires when bot has finished starting"""
        startup_info = f'{self.bot.user.name} has connected to Discord!'
        print(startup_info)
        logs.logger.info(startup_info)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                                 name='your events'))

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Fires when bot joins a guild. Sends a welcome message to the system channel."""
        try:
            guild_settings: database.Guild = await database.get_guild(guild)
            prefix = guild_settings.prefix
            welcome_message = (
                f'Hey! **{guild.name}**! I\'m here to alert you when an Epic RPG event pops up!\n'
                f'I\'m also trained in giving you snarky auto flex messages.\n\n'
                f'Note that all alerts are off by default. Use `/help` to get started.'
            )
            await guild.system_channel.send(welcome_message)
        except:
            return


# Initialization
def setup(bot):
    bot.add_cog(MainCog(bot))


# --- Embeds ---
async def embed_main_help(ctx: commands.Context) -> discord.Embed:
    """Main menu embed"""
    alert_settings = (
        f'{emojis.BP} `/settings` : Show the current settings\n'
        f'{emojis.BP} `/toggle alert` : Enable/disable alerts\n'
        f'{emojis.BP} `/set event-role` : Set an event ping role\n'
        f'{emojis.BP} `/set event-message` : Set an event message\n'
        f'{emojis.BP} `/set flex-channel` : Set the auto flex channel'
    )

    embed = discord.Embed(
        color = settings.EMBED_COLOR,
        title = 'TATL',
        description = 'Ding ding ding!'
    )
    embed.add_field(name='ALERTS', value=alert_settings, inline=False)

    return embed


async def embed_about(bot: commands.Bot, ctx: commands.Context, api_latency: datetime) -> discord.Embed:
    """Bot info embed"""
    general = (
        f'{emojis.BP} {len(bot.guilds):,} servers\n'
        f'{emojis.BP} {round(bot.latency * 1000):,} ms bot latency\n'
        f'{emojis.BP} {round(api_latency.total_seconds() * 1000):,} ms API latency'
    )
    creator = f'{emojis.BP} Miriel#0001'
    embed = discord.Embed(color = settings.EMBED_COLOR, title = 'ABOUT TATL')
    embed.add_field(name='BOT STATS', value=general, inline=False)
    embed.add_field(name='CREATOR', value=creator, inline=False)

    return embed