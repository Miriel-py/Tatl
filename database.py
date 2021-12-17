# database.py
"""Access to the database"""

from datetime import datetime
import sqlite3
from typing import NamedTuple, Optional, Union

import discord
from discord.ext import commands

from resources import exceptions, logs, settings, strings


ERG_DB = sqlite3.connect(settings.DB_FILE, isolation_level=None)


INTERNAL_ERROR_NO_DATA_FOUND = 'No data found in database.\nTable: {table}\nFunction: {function}\nSQL: {sql}'
INTERNAL_ERROR_SQLITE3 = 'Error executing SQL.\nError: {error}\nTable: {table}\nFunction: {function}\SQL: {sql}'
INTERNAL_ERROR_LOOKUP = 'Error assigning values.\nError: {error}\nTable: {table}\nFunction: {function}\Records: {record}'
INTERNAL_ERROR_NO_ARGUMENTS = 'You need to specify at least one keyword argument.\nTable: {table}\nFunction: {function}'


class GuildEvent(NamedTuple):
    name: str
    enabled: bool
    message: str
    role_id: int

class Guild(NamedTuple):
    id: int
    auto_flex_enabled: bool
    auto_flex_channel_id: int
    arena: GuildEvent
    boss: GuildEvent
    catch: GuildEvent
    chop: GuildEvent
    fish: GuildEvent
    miniboss: GuildEvent
    rumble: GuildEvent
    summon: GuildEvent


async def log_error(error: Union[Exception, str], ctx: Optional[discord.ApplicationContext] = None):
    """Logs an error to the database and the logfile

    Arguments
    ---------
    error: Exception or a simple string.
    ctx: If context is available, the function will log the user input, the message timestamp
    and the user settings. If not, current time is used, settings and input are logged as "N/A".

    Raises
    ------
    sqlite3.Error when something goes wrong in the database. Also logs this error to the log file.
    """
    table = 'errors'
    function_name = 'log_error'
    sql = 'INSERT INTO errors VALUES (?, ?, ?, ?)'
    if ctx is not None:
        command_name = f'{ctx.command.full_parent_name} {ctx.command.name}'.strip()
        timestamp = ctx.author.created_at
        user_options = str(ctx.interaction.data['options'])
    else:
        timestamp = datetime.utcnow()
        user_options = 'N/A'
    try:
        cur = ERG_DB.cursor()
        cur.execute(sql, (timestamp, command_name, user_options, str(error)))
    except sqlite3.Error as error:
        logs.logger.error(
            INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql),
            ctx
        )
        raise


# --- Database: Get Data ---
async def get_guild(ctx_or_guild: Union[discord.ApplicationContext, discord.Guild]) -> Guild:
    """Gets all guild settings.

    Returns
    -------
    Guild object

    Raises
    ------
    sqlite3.Error if something happened within the database.
    exceptions.NoDataFoundError if no guild was found.
    LookupError if something goes wrong reading the dict.
    Also logs all errors to the database.
    """
    table = 'settings_guild'
    function_name = 'get_guild'
    sql = 'SELECT * FROM settings_guild where guild_id=?'
    database_error = '{error}\nFunction: {function}'
    if isinstance(ctx_or_guild, (discord.ApplicationContext, commands.Context)):
        ctx = ctx_or_guild
        guild_id = ctx.guild.id
    else:
        ctx = None
        guild_id = ctx_or_guild.id
    try:
        cur = ERG_DB.cursor()
        cur.row_factory = sqlite3.Row
        cur.execute(sql, (guild_id,))
        record = cur.fetchone()
    except sqlite3.Error as error:
        await log_error(
            INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql),
            ctx
        )
        raise

    if not record:
        sql = 'INSERT INTO settings_guild (guild_id, prefix) VALUES (?, ?)'
        try:
            cur.execute(sql, (guild_id, settings.DEFAULT_PREFIX))
            sql = 'SELECT * FROM settings_guild where guild_id=?'
            cur.execute(sql, (guild_id,))
            record = cur.fetchone()
        except sqlite3.Error as error:
            await log_error(
                INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql),
                ctx
            )
            raise
    try:
        arena_settings = GuildEvent(
            name = 'Arena',
            enabled = bool(record['arena_enabled']),
            message = record['arena_message'] if record['arena_message'] is not None else strings.DEFAULT_MESSAGES['arena'],
            role_id = record['arena_role_id'],
        )
        boss_settings = GuildEvent(
            name = 'Legendary Boss',
            enabled = bool(record['boss_enabled']),
            message = record['boss_message'] if record['boss_message'] is not None else strings.DEFAULT_MESSAGES['legendary-boss'],
            role_id = record['boss_role_id'],
        )
        catch_settings = GuildEvent(
            name = 'Catch (Coin Rain)',
            enabled = bool(record['catch_enabled']),
            message = record['catch_message'] if record['catch_message'] is not None else strings.DEFAULT_MESSAGES['catch'],
            role_id = record['catch_role_id'],
        )
        chop_settings = GuildEvent(
            name = 'Chop (Epic Tree)',
            enabled = bool(record['chop_enabled']),
            message = record['chop_message'] if record['chop_message'] is not None else strings.DEFAULT_MESSAGES['chop'],
            role_id = record['chop_role_id'],
        )
        fish_settings = GuildEvent(
            name = 'Fish (Megalodon)',
            enabled = bool(record['fish_enabled']),
            message = record['fish_message'] if record['fish_message'] is not None else strings.DEFAULT_MESSAGES['fish'],
            role_id = record['fish_role_id'],
        )
        miniboss_settings = GuildEvent(
            name = 'Miniboss',
            enabled = bool(record['miniboss_enabled']),
            message = (
                record['miniboss_message'] if record['miniboss_message'] is not None else strings.DEFAULT_MESSAGES['miniboss']
            ),
            role_id = record['miniboss_role_id'],
        )
        rumble_settings = GuildEvent(
            name = 'Rumble Royale',
            enabled = bool(record['rumble_enabled']),
            message = record['rumble_message'] if record['rumble_message'] is not None else strings.DEFAULT_MESSAGES['rumble-royale'],
            role_id = record['rumble_role_id'],
        )
        summon_settings = GuildEvent(
            name = 'Lootbox Summoning',
            enabled = bool(record['summon_enabled']),
            message = record['summon_message'] if record['summon_message'] is not None else strings.DEFAULT_MESSAGES['summon'],
            role_id = record['summon_role_id'],
        )
        guild_settings = Guild(
            id = record['guild_id'],
            auto_flex_enabled = bool(record['auto_flex_enabled']),
            auto_flex_channel_id = record['auto_flex_channel_id'],
            arena = arena_settings,
            boss = boss_settings,
            catch = catch_settings,
            chop = chop_settings,
            fish = fish_settings,
            miniboss = miniboss_settings,
            rumble = rumble_settings,
            summon = summon_settings
        )
    except Exception as error:
        await log_error(
            INTERNAL_ERROR_LOOKUP.format(error=error, table=table, function=function_name, record=record),
            ctx
        )
        raise LookupError

    return guild_settings



# --- Database: Write Data ---
async def update_guild(ctx: discord.ApplicationContext, **kwargs) -> None:
    """Updates guild settings.

    Arguments
    ---------
    ctx: Context.
    kwargs (column=value):
        auto_flex_enabled: bool
        auto_flex_channel_id: int
        arena_enabled: bool
        arena_message: str
        arena_role_id: int
        boss_enabled: bool
        boss_message: str
        boss_role_id: int
        catch_enabled: bool
        catch_message: str
        catch_role_id: int
        chop_enabled: bool
        chop_message: str
        chop_role_id: int
        fish_enabled: bool
        fish_message: str
        fish_role_id: int
        miniboss_enabled: bool
        miniboss_message: str
        miniboss_role_id: int
        rumble_enabled: bool
        rumble_message: str
        rumble_role_id: int
        summon_enabled: bool
        summon_message: str
        summon_role_id: int

    Raises
    ------
    sqlite3.Error if something happened within the database.
    NoArgumentsError if not kwargs are passed (need to pass at least one)
    Also logs all error to the database.
    """
    table = 'settings_guild'
    function_name = 'update_guild'
    guild_id = ctx.guild.id
    if not kwargs:
        await log_error(
            INTERNAL_ERROR_NO_ARGUMENTS.format(table=table, function=function_name),
            ctx
        )
        raise exceptions.NoArgumentsError('You need to specify at least one keyword argument.')
    await get_guild(ctx) # Makes sure the user exists in the database
    try:
        cur = ERG_DB.cursor()
        sql = 'UPDATE settings_guild SET'
        for kwarg in kwargs:
            sql = f'{sql} {kwarg} = :{kwarg},'
        sql = sql.strip(",")
        kwargs['guild_id'] = guild_id
        sql = f'{sql} WHERE guild_id = :guild_id'
        cur.execute(sql, kwargs)
    except sqlite3.Error as error:
        await log_error(
            INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql),
            ctx
        )
        raise