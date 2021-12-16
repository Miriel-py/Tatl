# settings.py
"""Contains settings commands"""

import discord
from discord.commands import slash_command
from discord.enums import SlashCommandOptionType
from discord.commands import Option, SlashCommandGroup
from discord.ext import commands

import database
from resources import emojis, settings, strings


class SettingsCog(commands.Cog):
    """Cog user and guild settings commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    setting = SlashCommandGroup(
        "set",
        "Various settings",
    )

    setting_event = setting.create_subgroup(
        "event", "Event settings"
    )

    setting_autoflex = setting.create_subgroup(
        "auto-flex", "Auto-flex settings"
    )

    enable = SlashCommandGroup(
        "enable",
        "Enable alerts",
    )

    disable = SlashCommandGroup(
        "disable",
        "Disable alerts",
    )

    # Commands
    @commands.command(aliases=('setprefix',))
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True)
    async def prefix(self, ctx: commands.Context, *args: str) -> None:
        """Gets/sets new server prefix"""
        guild_settings: database.Guild = await database.get_guild(ctx)
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
            guild_settings: database.Guild = await database.get_guild(ctx)
            await ctx.send(f'Prefix changed to `{guild_settings.prefix}`')
        else:
            await ctx.send(
                f'The prefix for this server is `{guild_settings.prefix}`\n'
                f'To change the prefix, use `{syntax}`'
            )

    @slash_command(name='settings')
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def settings_command(self, ctx: discord.ApplicationContext) -> None:
        """Shows the current settings"""
        embed = await embed_guild_settings(self.bot, ctx)
        await ctx.respond(embed=embed)

    @enable.command(name='alert')
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def enable_alert(
        self,
        ctx: discord.ApplicationContext,
        event: Option(str, 'Event the alert should be enabled for', choices=strings.ALERTS_ALL),
    ) -> None:
        """Enables alerts"""

        alerts = strings.ALERTS if event == 'all' else [event,]
        update_alerts = {}
        updated_alerts = []
        for alert in alerts:
            alert_column = f'{strings.ALERT_COLUMNS[alert]}_enabled'
            update_alerts[alert_column] = True
            updated_alerts.append(alert)

        message_result = ''
        await database.update_guild(ctx, **update_alerts)
        message_updated_alerts = 'Enabled the following alerts:'
        for alert in updated_alerts:
            message_updated_alerts = f'{message_updated_alerts}\n{emojis.BP} `{alert}`'
        message_result = message_updated_alerts

        await ctx.respond(message_result)

    @disable.command(name='alert')
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def disable_alert(
        self,
        ctx: discord.ApplicationContext,
        event: Option(str, 'Event the alert should be disabled for', choices=strings.ALERTS_ALL),
    ) -> None:
        """Disables alerts"""

        alerts = strings.ALERTS if event == 'all' else [event,]
        update_alerts = {}
        updated_alerts = []
        for alert in alerts:
            alert_column = f'{strings.ALERT_COLUMNS[alert]}_enabled'
            update_alerts[alert_column] = False
            updated_alerts.append(alert)

        message_result = ''
        await database.update_guild(ctx, **update_alerts)
        message_updated_alerts = 'Disabled the following alerts:'
        for alert in updated_alerts:
            message_updated_alerts = f'{message_updated_alerts}\n{emojis.BP} `{alert}`'
        message_result = message_updated_alerts

        await ctx.respond(message_result)

    @setting_event.command(name='role')
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def set_event_role(
        self,
        ctx: discord.ApplicationContext,
        event: Option(str, 'Event the role is pinged for', choices=strings.ROLES_MESSAGES_ALL),
        role: Option(SlashCommandOptionType(8), 'Role to ping. If omitted, Tatl will ping @here.', required=False, default=None)
    ) -> None:
        """Sets the role that is pinged when an event is detected"""

        alerts = strings.ROLES_MESSAGES if event == 'all' else [event,]
        update_alerts = {}
        updated_alerts = []
        for alert in alerts:
            alert_column = f'{strings.ALERT_COLUMNS[alert]}_role_id'
            update_alerts[alert_column] = 0 if role is None else role.id
            updated_alerts.append(alert)

        message_result = ''
        await database.update_guild(ctx, **update_alerts)
        role_name = f'@{role.name}' if role is not None else '@here'
        message_updated_alerts = f'Updated the role to `{role_name}` for the following alerts:'
        for alert in updated_alerts:
            message_updated_alerts = f'{message_updated_alerts}\n{emojis.BP} `{alert}`'
        message_result = message_updated_alerts

        await ctx.respond(message_result)

    @setting_event.command(name='message')
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def set_event_message(
        self,
        ctx: discord.ApplicationContext,
        event: Option(str, 'Event the message is for', choices=strings.ROLES_MESSAGES_ALL),
        message: Option(str, 'Message to send. If omitted, message will reset to default.', required=False, default=None)
    ) -> None:
        """Set the message that is sent when an event is detected"""

        alerts = strings.ROLES_MESSAGES if event == 'all' else [event,]

        update_alerts = {}
        updated_alerts = []
        for alert in alerts:
            alert_column = f'{strings.ALERT_COLUMNS[alert]}_message'
            update_alerts[alert_column] = message if message != '' else strings.DEFAULT_MESSAGES[alert]
            updated_alerts.append(alert)

        message_result = ''
        await database.update_guild(ctx, **update_alerts)
        message_updated_alerts = 'Updated the message for the following alerts:'
        for alert in updated_alerts:
            message_updated_alerts = f'{message_updated_alerts}\n{emojis.BP} `{alert}`'
        message_result = message_updated_alerts

        await ctx.respond(message_result)

    @setting_autoflex.command(name='channel')
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def set_autoflex_channel(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(discord.TextChannel, 'Channel the auto-flex messages are sent to')
    ) -> None:
        """Sets the auto-flex channel"""

        await database.update_guild(ctx, auto_flex_channel_id=channel.id)
        await ctx.respond(f'Changed the auto-flex channel to `{channel.name}`')


# Initialization
def setup(bot):
    bot.add_cog(SettingsCog(bot))


# --- Embeds ---
async def embed_guild_settings(bot: commands.Bot, ctx: commands.Context) -> discord.Embed:
    """Settings embed"""
    guild_settings: database.Guild = await database.get_guild(ctx)

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