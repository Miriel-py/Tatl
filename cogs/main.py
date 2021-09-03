# main.py
"""Contains error handling and the help and about commands"""

import aiohttp
from datetime import datetime
import gettext
from typing import Tuple

import discord
from discord.ext import commands, tasks

import database
from resources import emojis, exceptions, logs, settings, strings


_ = gettext.gettext


class MainCog(commands.Cog):
    """Cog with events and help and about commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Commands
    @commands.command(name='help',aliases=('guide','g','h',))
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def main_help(self, ctx: commands.Context):
        """Main help command"""
        prefix = await database.get_prefix(ctx)
        embed = await embed_main_help(ctx)
        await ctx.send(embed=embed)

    @commands.command(aliases=('statistic','statistics,','devstat','ping','devstats','info','stats'))
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def about(self, ctx: commands.Context):
        """Shows some bot info"""
        start_time = datetime.utcnow()
        message = await ctx.send(_('Testing API latency...'))
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
            embed = discord.Embed(title=_('An error occured'))
            embed.add_field(name=_('Command'), value=f'`{ctx.command.qualified_name}`', inline=False)
            embed.add_field(name=_('Error'), value=f'```py\n{error}\n```', inline=False)
            await ctx.send(embed=embed)

        if isinstance(error, (commands.CommandNotFound, exceptions.FirstTimeUserError, commands.NotOwner)):
            return
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(
                _('Command `{cmd_name}` is temporarily disabled.').format(cmd_name=ctx.command.qualified_name)
            )
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
            if settings.DEBUG_MODE:
                await send_error()
            else:
                await ctx.send(strings.MSG_ERROR)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Fires when bot has finished starting"""
        #DiscordComponents(bot)
        startup_info = f'{self.bot.user.name} has connected to Discord!'
        print(startup_info)
        logs.logger.info(startup_info)
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                                 name='your questions'))
        await self.update_stats.start()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Sends welcome message on guild join"""
        try:
            prefix = await database.get_prefix(self.bot, guild)
            welcome_message = _(
                'Hello **{guild_name}**! I\'m here to provide some guidance!\n\n'
                'To get a list of all topics, type `{prefix}guide` (or `{prefix}g` for short).\n'
                'If you don\'t like this prefix, use `{prefix}setprefix` to change it.\n\n'
                'Tip: If you ever forget the prefix, simply ping me with a command.'
            )
            await guild.system_channel.send(welcome_message.format(guild_name=guild.name, prefix=prefix))
        except:
            return


# Initialization
def setup(bot):
    bot.add_cog(MainCog(bot))


# --- Embeds ---
async def embed_main_help(ctx: commands.Context) -> discord.Embed:
    """Main menu embed"""
    prefix = ctx.prefix

    progress = (
        f'{emojis.BP} `{prefix}start` : {_("Starter guide for new players")}\n'
        f'{emojis.BP} `{prefix}areas` / `{prefix}a` : {_("Area guides overview")}\n'
        f'{emojis.BP} `{prefix}dungeons` / `{prefix}d` : {_("Dungeon guides overview")}\n'
        f'{emojis.BP} `{prefix}timetravel` / `{prefix}tt` : {_("Time travel guide")}\n'
        f'{emojis.BP} `{prefix}coolness` : {_("Everything about coolness")}'
    )
    crafting = (
        f'{emojis.BP} `{prefix}craft` : {_("Recipes mats calculator")}\n'
        f'{emojis.BP} `{prefix}dismantle` / `{prefix}dm` : {_("Dismantling calculator")}\n'
        f'{emojis.BP} `{prefix}invcalc` / `{prefix}ic` : {_("Inventory calculator")}\n'
        f'{emojis.BP} `{prefix}drops` : {_("Monster drops")}\n'
        f'{emojis.BP} `{prefix}enchants` / `{prefix}e` : {_("All possible enchants")}'
    )
    animals = (
        f'{emojis.BP} `{prefix}horse` : {_("Horse guide")}\n'
        f'{emojis.BP} `{prefix}pet` : {_("Pets guide")}\n'
    )
    trading = f'{emojis.BP} `{prefix}trading` : {_("Trading guides overview")}'
    professions_value = f'{emojis.BP} `{prefix}professions` / `{prefix}pr` : {_("Professions guide")}'
    guild_overview = f'{emojis.BP} `{prefix}guild` : {_("Guild guide")}'
    event_overview = f'{emojis.BP} `{prefix}events` : {_("Event guides overview")}'
    monsters = (
        f'{emojis.BP} `{prefix}mobs [area]` : {_("List of all monsters in area [area]")}\n'
        f'{emojis.BP} `{prefix}dailymob` : {_("Where to find the daily monster")}'
    )
    gambling_overview = f'{emojis.BP} `{prefix}gambling` : {_("Gambling guides overview")}'
    misc = (
        f'{emojis.BP} `{prefix}calc` : {_("A basic calculator")}\n'
        f'{emojis.BP} `{prefix}codes` : {_("Currently valid redeemable codes")}\n'
        f'{emojis.BP} `{prefix}duel` : {_("Duelling weapons")}\n'
        f'{emojis.BP} `{prefix}farm` : {_("Farming guide")}\n'
        f'{emojis.BP} `{prefix}tip` : {_("A handy dandy random tip")}'
    )
    botlinks = (
        f'{emojis.BP} `{prefix}invite` : {_("Invite me to your server")}\n'
        f'{emojis.BP} `{prefix}support` : {_("Visit the support server")}\n'
        f'{emojis.BP} `{prefix}links` : {_("EPIC RPG wiki & support")}'
    )
    settings = (
        f'{emojis.BP} `{prefix}settings` / `{prefix}me` : {_("Check your user settings")}\n'
        f'{emojis.BP} `{prefix}setprogress` / `{prefix}sp` : {_("Change your user settings")}\n'
        f'{emojis.BP} `{prefix}prefix` : {_("Check/change the prefix")}'
    )
    embed = discord.Embed(
        color = settings.EMBED_COLOR,
        title = 'EPIC RPG GUIDE',
        description = _('Hey **{user_name}**, what do you want to know?').format(user_name=ctx.author.name)
    )
    embed.set_footer(text=_('Note: This is not an official guide bot.'))
    embed.add_field(name=_('PROGRESS'), value=progress, inline=False)
    embed.add_field(name=_('CRAFTING'), value=crafting, inline=False)
    embed.add_field(name=_('HORSE & PETS'), value=animals, inline=False)
    embed.add_field(name=_('TRADING'), value=trading, inline=False)
    embed.add_field(name=_('PROFESSIONS'), value=professions_value, inline=False)
    embed.add_field(name=_('GUILD'), value=guild_overview, inline=False)
    embed.add_field(name=_('EVENTS'), value=event_overview, inline=False)
    embed.add_field(name=_('MONSTERS'), value=monsters, inline=False)
    embed.add_field(name=_('GAMBLING'), value=gambling_overview, inline=False)
    embed.add_field(name=_('MISC'), value=misc, inline=False)
    embed.add_field(name=_('LINKS'), value=botlinks, inline=False)
    embed.add_field(name=_('SETTINGS'), value=settings, inline=False)

    return embed


async def embed_about(bot: commands.Bot, ctx: commands.Context, api_latency: datetime) -> discord.Embed:
    """Bot info embed"""
    user_count, *x = await database.get_user_count(ctx)
    closed_shards = 0
    for shard_id in bot.shards:
        if bot.get_shard(shard_id).is_closed():
            closed_shards += 1
    general = (
        f'{emojis.BP} {len(bot.guilds):,} {_("servers")}\n'
        f'{emojis.BP} {user_count:,} {_("users")}\n'
        f'{emojis.BP} {len(bot.shards):,} {_("shards")} ({closed_shards:,} {_("shards offline")})\n'
        f'{emojis.BP} {round(bot.latency * 1000):,} ms {_("average latency")}'
    )
    current_shard = bot.get_shard(ctx.guild.shard_id)
    current_shard_status = (
        f'{emojis.BP} {_("Shard")}: {current_shard.id + 1} of {len(bot.shards):,}\n'
        f'{emojis.BP} {_("Bot latency")}: {round(current_shard.latency * 1000):,} ms\n'
        f'{emojis.BP} {_("API latency")}: {round(api_latency.total_seconds() * 1000):,} ms'
    )
    creator = f'{emojis.BP} Miriel#0001'
    thanks = (
        f'{emojis.BP} FlyingPanda#0328\n'
        f'{emojis.BP} {_("All the math geniuses in the support server")}'
    )
    embed = discord.Embed(color = settings.EMBED_COLOR, title = _('ABOUT EPIC RPG GUIDE'))
    embed.add_field(name=_('BOT STATS'), value=general, inline=False)
    embed.add_field(name=_('CURRENT SHARD'), value=current_shard_status, inline=False)
    embed.add_field(name=_('CREATOR'), value=creator, inline=False)
    embed.add_field(name=_('SPECIAL THANKS TO'), value=thanks, inline=False)

    return embed