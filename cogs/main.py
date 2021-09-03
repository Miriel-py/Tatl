# main.py
"""Contains error handling and the help and about commands"""

from datetime import datetime

import discord
from discord.ext import commands, tasks

import database
from resources import emojis, exceptions, logs, settings


class MainCog(commands.Cog):
    """Cog with events and help and about commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands
    @commands.command(name='help',aliases=('h',))
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def main_help(self, ctx: commands.Context) -> None:
        """Main help command"""
        embed = await embed_main_help(ctx)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(aliases=('statistic','statistics,','devstat','ping','devstats','info','stats'))
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def about(self, ctx: commands.Context):
        """Shows some bot info"""
        start_time = datetime.utcnow()
        message = await ctx.send('Testing API latency...')
        end_time = datetime.utcnow()
        api_latency = end_time - start_time
        embed = await embed_about(self.bot, ctx, api_latency)
        await message.edit(content=None, embed=embed)

     # Events
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """Runs when an error occurs and handles them accordingly.
        Interesting errors get written to the database for further review.
        """
        async def send_error() -> None:
            """Sends error message as embed"""
            embed = discord.Embed(title='An error occured')
            embed.add_field(name='Command', value=f'`{ctx.command.qualified_name}`', inline=False)
            embed.add_field(name='Error', value=f'```py\n{error}\n```', inline=False)
            await ctx.send(embed=embed)

        if isinstance(error, (commands.CommandNotFound, commands.NotOwner)):
            return
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f'Command `{ctx.command.qualified_name}` is temporarily disabled.')
        elif isinstance(error, (commands.MissingPermissions, commands.MissingRequiredArgument,
                                commands.TooManyArguments, commands.BadArgument)):
            await send_error()
        elif isinstance(error, commands.BotMissingPermissions):
            if 'send_messages' in error.missing_perms:
                return
            if 'embed_links' in error.missing_perms:
                await ctx.send(error)
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
            guild_settings = database.Guild
            guild_settings = await database.get_guild(guild)
            prefix = guild_settings.prefix
            welcome_message = (
                f'Hey! **{guild.name}**! I\'m here to alert you when an Epic RPG event pops up!\n'
                f'I\'m also trained in giving you snarky auto flex messages.\n\n'
                f'Note that all alerts are off by default. Use `{prefix}help` to get started.\n'
                f'If you don\'t like this prefix, use `{prefix}prefix` to change it.\n\n'
                f'Tip: If you ever forget the prefix, simply ping me with a command.'
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
    prefix = ctx.prefix
    alert_settings = (
        f'{emojis.BP} `{prefix}settings` : Show the current settings\n'
        f'{emojis.BP} `{prefix}enable` / `disable` : Enable/disable alerts\n'
        f'{emojis.BP} `{prefix}event-role` : Set an event ping role\n'
        f'{emojis.BP} `{prefix}event-message` : Set an event message\n'
        f'{emojis.BP} `{prefix}flex-channel` : Set the auto flex channel'
    )
    prefix_settings = (
        f'{emojis.BP} `{prefix}prefix` : Check/set the bot prefix\n'
    )

    embed = discord.Embed(
        color = settings.EMBED_COLOR,
        title = 'TATL',
        description = 'Ding ding ding!'
    )
    embed.add_field(name='ALERTS', value=alert_settings, inline=False)
    embed.add_field(name='PREFIX', value=prefix_settings, inline=False)

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