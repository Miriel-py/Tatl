# settings.py
"""Contains settings commands"""

import asyncio

import discord
from discord.ext import commands

import database
from resources import emojis, settings, strings


class SettingsCog(commands.Cog):
    """Cog user and guild settings commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Commands
    @commands.command(aliases=('setprefix',))
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True)
    async def prefix(self, ctx: commands.Context, *args: str) -> None:
        """Gets/sets new server prefix"""
        guild_settings = database.Guild
        guild_settings = await database.get_guild(ctx)
        prefix = guild_settings.prefix
        syntax = f'{prefix}prefix <prefix>'
        message_syntax = (
            f'{strings.MSG_SYNTAX.format(syntax=syntax)}\n\n'
            f'Tip: If you want to include a space, use quotation marks.\n'
            f'Examples:\n• `{prefix}prefix "tatl "`\n• `{prefix}setprefix &`'
        )
        if args:
            if len(args) > 1:
                await ctx.send(message_syntax)
                return
            (new_prefix,) = args
            await database.update_guild(ctx, prefix=new_prefix)
            guild_settings = database.Guild
            guild_settings = await database.get_guild(ctx)
            await ctx.send(f'Prefix changed to `{guild_settings.prefix}`')
        else:
            await ctx.send(
                f'The prefix for this server is `{guild_settings.prefix}`\n'
                f'To change the prefix, use `{syntax}`'
            )

    @commands.command()
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def settings(self, ctx: commands.Context) -> None:
        """Returns current user progress settings"""
        embed = await embed_guild_settings(self.bot, ctx)
        await ctx.send(embed=embed)

    @commands.command(aliases=('disable',))
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def enable(self, ctx: commands.Context, *args: str) -> None:
        """Enables/disables alerts"""
        prefix = ctx.prefix
        syntax = f'{prefix}enable/disable <alert>'
        alert_list = f'Available alerts:\n{emojis.BP} `all`'
        for alert in strings.ALERTS:
            alert_list = f'{alert_list}\n{emojis.BP} `{alert}`'
        message_syntax = (
            f'{strings.MSG_SYNTAX.format(syntax=syntax)}\n\n'
            f'{alert_list}'
        )

        if not args:
            await ctx.reply(message_syntax, mention_author=False)
            return

        args = [arg.lower() for arg in args]
        if args[0] == 'all':
            args = strings.ALERTS
        action = ctx.invoked_with.lower()
        update_alerts = {}
        updated_alerts, ignored_alerts = [], []
        for alert in args:
            if alert in strings.ALERT_ALIASES:
                alert = strings.ALERT_ALIASES[alert]
            if alert in strings.ALERTS:
                alert_column = f'{strings.ALERT_COLUMNS[alert]}_enabled'
                update_alerts[alert_column] = True if action == 'enable' else False
                updated_alerts.append(alert)
            else:
                ignored_alerts.append(alert)

        message_result = ''
        if updated_alerts:
            await database.update_guild(ctx, **update_alerts)
            message_updated_alerts = f'{action.capitalize()}d the following alerts:'
            for alert in updated_alerts:
                message_updated_alerts = f'{message_updated_alerts}\n{emojis.BP} `{alert}`'
            message_result = message_updated_alerts
        if ignored_alerts:
            message_ignored_alerts = 'Could not find alerts with the following names:'
            for ignored_alert in ignored_alerts:
                message_ignored_alerts = f'{message_ignored_alerts}\n{emojis.BP} `{ignored_alert}`'
            message_result = f'{message_result}\n\n{message_ignored_alerts}'.strip()

        if message_result == '': message_result = message_syntax
        await ctx.reply(message_result, mention_author=False)

    @commands.command(name='event-role', aliases=('role',))
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def event_role(self, ctx: commands.Context, *args: str) -> None:
        """Sets/resets event ping roles"""
        prefix = ctx.prefix
        syntax = f'{prefix}event-role <event> <@role>'
        alert_list = f'Available alerts:\n{emojis.BP} `all`'
        for alert in strings.ALERTS:
            alert_list = f'{alert_list}\n{emojis.BP} `{alert}`'
        message_syntax = (
            f'{strings.MSG_SYNTAX.format(syntax=syntax)}\n\n'
            f'{alert_list}'
        )

        if not args:
            await ctx.reply(f'This command updates the pinged role when an event occurs.\n{message_syntax}', mention_author=False)
            return
        if not len(args) == 2:
            await ctx.reply(message_syntax, mention_author=False)
            return

        args = [arg.lower() for arg in args]
        arg_alert, arg_role = args
        if arg_role == '@everyone':
            role_id = ctx.guild.id
        elif arg_role == '@here':
            role_id = 0
        else:
            role_id = arg_role.replace('<@&','').replace('>','')
        try:
            role_id = int(role_id)
        except:
            await ctx.reply(f'Invalid role.\n{message_syntax}', mention_author=False)
            return
        if role_id not in (0, ctx.guild.id):
            role = ctx.guild.get_role(role_id)
            if role is None:
                await ctx.reply(f'Invalid role.\n{message_syntax}', mention_author=False)
                return
        alerts = strings.ROLES_MESSAGES if arg_alert == 'all' else [arg_alert,]

        update_alerts = {}
        ignored_alerts, updated_alerts = [], []
        for alert in alerts:
            if alert in strings.ALERT_ALIASES:
                alert = strings.ALERT_ALIASES[alert]
            if alert in strings.ALERTS:
                alert_column = f'{strings.ALERT_COLUMNS[alert]}_role_id'
                update_alerts[alert_column] = role_id
                updated_alerts.append(alert)
            else:
                ignored_alerts.append(alert)

        message_result = ''
        if updated_alerts:
            await database.update_guild(ctx, **update_alerts)
            message_updated_alerts = 'Updated the role for the following alerts:'
            for alert in updated_alerts:
                message_updated_alerts = f'{message_updated_alerts}\n{emojis.BP} `{alert}`'
            message_result = message_updated_alerts
        if ignored_alerts:
            message_ignored_alerts = 'Could not find alerts with the following names:'
            for ignored_alert in ignored_alerts:
                message_ignored_alerts = f'{message_ignored_alerts}\n{emojis.BP} `{ignored_alert}`'
            message_result = f'{message_result}\n\n{message_ignored_alerts}'.strip()

        if message_result == '': message_result = message_syntax
        await ctx.reply(message_result, mention_author=False)

    @commands.command(name='event-message', aliases=('message',))
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def event_message(self, ctx: commands.Context, *args: str) -> None:
        """Sets/resets event messages"""
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        prefix = ctx.prefix
        syntax = f'{prefix}event-message <event> [<message>|reset]'
        alert_list = f'Available alerts:\n{emojis.BP} `all`'
        for alert in strings.ALERTS:
            alert_list = f'{alert_list}\n{emojis.BP} `{alert}`'
        message_syntax = (
            f'{strings.MSG_SYNTAX.format(syntax=syntax)}\n\n'
            f'{alert_list}'
        )

        if not args:
            await ctx.reply(f'This command updates or resets the message that is sent when an event occurs.\n{message_syntax}', mention_author=False)
            return

        arg_alert, *arg_message = args
        arg_alert = arg_alert.lower()
        reset = False
        if len(args) == 2 and arg_message[0].lower() == 'reset':
            reset = True
            message = None
            del arg_message[0]
        if not reset:
            if arg_message:
                message = ''
                for arg in arg_message:
                    message = f'{message} {arg}'
            else:
                await ctx.reply(f'**{ctx.author.name}**, please enter the alert message your want to set: (type `abort` to abort)', mention_author=False)
                try:
                    answer = await self.bot.wait_for('message', check=check, timeout=60)
                except asyncio.TimeoutError as error:
                    await ctx.send(f'**{ctx.author.name}**, you didn\'t answer in time.')
                    return
                if answer.content.lower() in ('abort','cancel'):
                    await ctx.send('Aborted.')
                    return
                message = answer.content
            message = message.strip()
        alerts = strings.ROLES_MESSAGES if arg_alert == 'all' else [arg_alert,]

        update_alerts = {}
        ignored_alerts, updated_alerts = [], []
        for alert in alerts:
            if alert in strings.ALERT_ALIASES:
                alert = strings.ALERT_ALIASES[alert]
            if alert in strings.ALERTS:
                alert_column = f'{strings.ALERT_COLUMNS[alert]}_message'
                update_alerts[alert_column] = message
                updated_alerts.append(alert)
            else:
                ignored_alerts.append(alert)

        message_result = ''
        if updated_alerts:
            await database.update_guild(ctx, **update_alerts)
            message_updated_alerts = 'Udated the message for the following alerts:'
            for alert in updated_alerts:
                message_updated_alerts = f'{message_updated_alerts}\n{emojis.BP} `{alert}`'
            message_result = message_updated_alerts
        if ignored_alerts:
            message_ignored_alerts = 'Could not find alerts with the following names:'
            for ignored_alert in ignored_alerts:
                message_ignored_alerts = f'{message_ignored_alerts}\n{emojis.BP} `{ignored_alert}`'
            message_result = f'{message_result}\n\n{message_ignored_alerts}'.strip()

        if message_result == '': message_result = message_syntax
        await ctx.reply(message_result, mention_author=False)

    @commands.command(name='flex-channel', aliases=('channel','flex',))
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def flex_channel(self, ctx: commands.Context, *args: str) -> None:
        """Sets/resets the auto flex channel"""
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        prefix = ctx.prefix
        syntax = f'{prefix}flex-channel <#channel>'
        message_syntax = (
            f'{strings.MSG_SYNTAX.format(syntax=syntax)}'
        )

        if args:
            channel_id = args[0].replace('<#','').replace('>','')
            try:
                channel_id = int(channel_id)
            except:
                await ctx.reply(f'Invalid channel.\n{message_syntax}', mention_author=False)
                return
            channel = ctx.guild.get_channel(channel_id)
            if channel is None:
                await ctx.reply(f'Invalid channel.\n{message_syntax}', mention_author=False)
                return

        if not args:
            await ctx.reply(f'**{ctx.author.name}**, do you want to set the current channel as the auto flex channel? [`yes/no`]', mention_author=False)
            try:
                answer = await self.bot.wait_for('message', check=check, timeout=60)
            except asyncio.TimeoutError as error:
                await ctx.send(f'**{ctx.author.name}**, you didn\'t answer in time.')
                return
            if answer.content.lower() in ('yes','y'):
                channel = ctx.channel
            else:
                await ctx.send('Aborted.')
                return

        await database.update_guild(ctx, auto_flex_channel_id=channel.id)
        await ctx.send(f'Changed the auto flex channel to `{channel.name}`')


# Initialization
def setup(bot):
    bot.add_cog(SettingsCog(bot))


# --- Embeds ---
async def embed_guild_settings(bot: commands.Bot, ctx: commands.Context) -> discord.Embed:
    """Settings embed"""
    guild_settings = database.Guild
    guild_settings = await database.get_guild(ctx)

    embed = discord.Embed(
        color = settings.EMBED_COLOR,
        title = 'SETTINGS'
    )

    auto_flex_enabled = 'Enabled' if guild_settings.auto_flex_enabled else 'Disabled'
    if not guild_settings.auto_flex_channel_id == 0:
        auto_flex_channel_name = ctx.guild.get_channel(guild_settings.auto_flex_channel_id).name
    else:
        auto_flex_channel_name = None
    auto_flex_field = (
        f'{emojis.BP} Alerts: `{auto_flex_enabled}`\n'
        f'{emojis.BP} Channel: `{auto_flex_channel_name}`'
    )
    embed.add_field(name='AUTO FLEX', value=auto_flex_field, inline=False)

    for setting in guild_settings:
        if isinstance(setting, database.GuildEvent):
            event_name = setting.name.upper()
            event_enabled = 'Enabled' if setting.enabled else 'Disabled'
            event_role_name = '@here' if setting.role_id == 0 else ctx.guild.get_role(setting.role_id).mention
            event_field = (
                f'{emojis.BP} Alerts: `{event_enabled}`\n'
                f'{emojis.BP} Message: {setting.message}\n'
                f'{emojis.BP} Ping role: {event_role_name}\n'
            )
            embed.add_field(name=event_name, value=event_field, inline=False)

    return embed