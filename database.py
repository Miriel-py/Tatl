# database.py
"""Access to the database"""

from datetime import datetime
import itertools
import sqlite3
from typing import List, NamedTuple, Optional, Tuple, Union

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
    prefix: str
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


async def mixed_case(*args: str) -> List[str]:
    """Generates mixed case prefixes"""
    mixed_prefixes = []
    for string in args:
        all_prefixes = map(''.join, itertools.product(*((c.upper(), c.lower()) for c in string)))
        for prefix in list(all_prefixes):
            mixed_prefixes.append(prefix)

    return mixed_prefixes


async def log_error(error: Union[Exception, str], ctx: Optional[commands.Context] = None):
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
    sql = 'INSERT INTO errors VALUES (?, ?, ?'
    if ctx is not None:
        timestamp = ctx.message.created_at
        user_input = ctx.message.content
    else:
        timestamp = datetime.utcnow()
        user_input = 'N/A'
    try:
        cur = ERG_DB.cursor()
        cur.execute(sql, (timestamp, user_input, str(error)))
    except sqlite3.Error as error:
        logs.logger.error(
            INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql),
            ctx
        )
        raise


# --- Database: Get Data ---
async def get_prefix_all(bot: commands.Bot, ctx: commands.Context) -> Tuple:
    """Gets all prefixes. If no prefix is found, a record for the guild is created with the
    default prefix.

    Returns
    -------
    A tuple with the current server prefix and the pingable bot

    Raises
    ------
    sqlite3.Error if something happened within the database.  Also logs this error to the database.
    """
    table = 'settings_guild'
    function_name = 'get_all_prefixes'
    sql = 'SELECT prefix FROM settings_guild where guild_id=?'
    guild_id = ctx.guild.id
    try:
        cur = ERG_DB.cursor()
        cur.execute(sql, (guild_id,))
        record = cur.fetchone()
        if record:
            prefix_db = record[0].replace('"','')
            prefixes = await mixed_case(prefix_db)
        else:
            sql = 'INSERT INTO settings_guild VALUES (?, ?)'
            cur.execute(sql, (guild_id, settings.DEFAULT_PREFIX,))
            prefixes = await mixed_case(settings.DEFAULT_PREFIX)
    except sqlite3.Error as error:
        await log_error(
            INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql),
            ctx
        )
        raise

    return commands.when_mentioned_or(*prefixes)(bot, ctx)


async def get_guild(ctx: commands.Context) -> Guild:
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
    try:
        cur = ERG_DB.cursor()
        cur.row_factory = sqlite3.Row
        cur.execute(sql, (ctx.guild.id,))
        record = cur.fetchone()
    except sqlite3.Error as error:
        await log_error(
            INTERNAL_ERROR_SQLITE3.format(error=error, table=table, function=function_name, sql=sql),
            ctx
        )
        raise

    if not record:
        await log_error(
            INTERNAL_ERROR_NO_DATA_FOUND.format(table=table, function=function_name, sql=sql),
            ctx
        )
        raise exceptions.NoDataFoundError
    try:
        arena_settings = GuildEvent(
            name = 'Arena',
            enabled = bool(record['arena_enabled']),
            message = record['arena_message'] if record['arena_message'] is not None else strings.DEFAULT_MSG_ARENA,
            role_id = record['arena_role_id'],
        )
        boss_settings = GuildEvent(
            name = 'Legendary Boss',
            enabled = bool(record['boss_enabled']),
            message = record['boss_message'] if record['boss_message'] is not None else strings.DEFAULT_MSG_BOSS,
            role_id = record['boss_role_id'],
        )
        catch_settings = GuildEvent(
            name = 'Catch (Coin Rain)',
            enabled = bool(record['catch_enabled']),
            message = record['catch_message'] if record['catch_message'] is not None else strings.DEFAULT_MSG_CATCH,
            role_id = record['catch_role_id'],
        )
        chop_settings = GuildEvent(
            name = 'Chop (Epic Tree)',
            enabled = bool(record['chop_enabled']),
            message = record['chop_message'] if record['chop_message'] is not None else strings.DEFAULT_MSG_CHOP,
            role_id = record['chop_role_id'],
        )
        fish_settings = GuildEvent(
            name = 'Fish (Megalodon)',
            enabled = bool(record['fish_enabled']),
            message = record['fish_message'] if record['fish_message'] is not None else strings.DEFAULT_MSG_FISH,
            role_id = record['fish_role_id'],
        )
        miniboss_settings = GuildEvent(
            name = 'Miniboss',
            enabled = bool(record['miniboss_enabled']),
            message = (
                record['miniboss_message'] if record['miniboss_message'] is not None else strings.DEFAULT_MSG_MINIBOSS
            ),
            role_id = record['miniboss_role_id'],
        )
        rumble_settings = GuildEvent(
            name = 'Rumble Royale',
            enabled = bool(record['rumble_enabled']),
            message = record['rumble_message'] if record['rumble_message'] is not None else strings.DEFAULT_MSG_RUMBLE,
            role_id = record['rumble_role_id'],
        )
        summon_settings = GuildEvent(
            name = 'Lootbox Summoning',
            enabled = bool(record['summon_enabled']),
            message = record['summon_message'] if record['summon_message'] is not None else strings.DEFAULT_MSG_SUMMON,
            role_id = record['summon_role_id'],
        )
        guild_settings = Guild(
            id = record['guild_id'],
            prefix = record['prefix'],
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
        await log_error(INTERNAL_ERROR_LOOKUP.format(error=error, table=table, function=function_name, record=record))
        raise LookupError

    return guild_settings



# --- Database: Write Data ---
async def update_guild(ctx: commands.Context, **kwargs) -> None:
    """Updates guild settings.

    Arguments
    ---------
    ctx: Context.
    kwargs (column=value):
        prefix: str
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
            INTERNAL_ERROR_NO_ARGUMENTS.format(error=error, table=table, function=function_name),
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






# Set event role
async def set_event_role(ctx, event_role, event):

    if event == 'all':
        sql =   'UPDATE settings_guild SET arena_role_id = ?, boss_role_id = ?, catch_role_id = ?, chop_role_id = ?, fish_role_id = ?,\
                miniboss_role_id = ?, summon_role_id = ? WHERE guild_id = ?'
    elif event == 'arena':
        sql = 'UPDATE settings_guild SET arena_role_id = ? WHERE guild_id = ?'
    elif event == 'legendary-boss':
        event = 'legendary boss'
        sql = 'UPDATE settings_guild SET boss_role_id = ? WHERE guild_id = ?'
    elif event == 'catch':
        sql = 'UPDATE settings_guild SET catch_role_id = ? WHERE guild_id = ?'
    elif event == 'chop':
        sql = 'UPDATE settings_guild SET chop_role_id = ? WHERE guild_id = ?'
    elif event == 'fish':
        sql = 'UPDATE settings_guild SET fish_role_id = ? WHERE guild_id = ?'
    elif event == 'miniboss':
        sql = 'UPDATE settings_guild SET miniboss_role_id = ? WHERE guild_id = ?'
    elif event == 'lootbox':
        event = 'lootbox summoning'
        sql = 'UPDATE settings_guild SET summon_role_id = ? WHERE guild_id = ?'
    elif event == 'rumble-royale':
        event = 'rumble royale'
        sql = 'UPDATE settings_guild SET rumble_role_id = ? WHERE guild_id = ?'

    try:
        if event_role in (0,1):
            event_role_id = event_role
        else:
            event_role_id = event_role.id

        cur=erg_db.cursor()
        cur.execute('SELECT arena_role_id FROM settings_guild WHERE guild_id=?', (ctx.guild.id,))
        record = cur.fetchone()

        if record:
            if event == 'all':
                cur.execute(sql, (event_role_id, event_role_id, event_role_id, event_role_id, event_role_id, event_role_id, event_role_id, ctx.guild.id,))
            else:
                cur.execute(sql, (event_role_id, ctx.guild.id,))

            if not event_role == 0:
                if event == 'all':
                    status = f'**{ctx.author.name}**, the role `{event_role.name}` is now set as your ping role for **all** events.'
                else:
                    status = f'**{ctx.author.name}**, the role `{event_role.name}` is now set as your ping role for {event} events.'
            else:
                if event == 'all':
                    status = f'**{ctx.author.name}**, the event role for **all** events was reset.\nPlease note that the bot will ping the role `@here` if no other role is set and alerts are enabled.'
                else:
                    status = f'**{ctx.author.name}**, the event role for {event} events was reset.\nPlease note that the bot will ping the role `@here` if no other role is set and alerts are enabled.'
        else:
            status = f'**{ctx.author.name}**, you have never used the bot on this server before. Please try again.'
    except sqlite3.Error as error:
        await log_error(ctx, error)

    return status

# Set event message
async def set_event_message(ctx, event_message, event):

    if event == 'all':
        sql =   'UPDATE settings_guild SET arena_message = ?, boss_message = ?, catch_message = ?, chop_message = ?, fish_message = ?,\
                miniboss_message = ?, summon_message = ? WHERE guild_id = ?'
    elif event == 'arena':
        sql = 'UPDATE settings_guild SET arena_message = ? WHERE guild_id = ?'
    elif event == 'legendary-boss':
        event = 'legendary boss'
        sql = 'UPDATE settings_guild SET boss_message = ? WHERE guild_id = ?'
    elif event == 'catch':
        sql = 'UPDATE settings_guild SET catch_message = ? WHERE guild_id = ?'
    elif event == 'chop':
        sql = 'UPDATE settings_guild SET chop_message = ? WHERE guild_id = ?'
    elif event == 'fish':
        sql = 'UPDATE settings_guild SET fish_message = ? WHERE guild_id = ?'
    elif event == 'miniboss':
        sql = 'UPDATE settings_guild SET miniboss_message = ? WHERE guild_id = ?'
    elif event == 'lootbox':
        event = 'lootbox summoning'
        sql = 'UPDATE settings_guild SET summon_message = ? WHERE guild_id = ?'
    elif event == 'rumble-royale':
        event = 'rumble royale'
        sql = 'UPDATE settings_guild SET rumble_message = ? WHERE guild_id = ?'

    try:
        cur=erg_db.cursor()
        cur.execute('SELECT arena_message FROM settings_guild WHERE guild_id=?', (ctx.guild.id,))
        record = cur.fetchone()

        if record:
            if event == 'all':
                cur.execute(sql, (event_message, event_message, event_message, event_message, event_message, event_message, event_message, ctx.guild.id,))
            else:
                cur.execute(sql, (event_message, ctx.guild.id,))


            if not event_message == None:
                if event == 'all':
                    status = (
                        f'**{ctx.author.name}**, the alert message for **all** events is now set to the following:\n'
                        f'{emojis.bp} {event_message}'
                    )
                else:
                    status = (
                        f'**{ctx.author.name}**, the alert message for {event} events is now set to the following:\n'
                        f'{emojis.bp} {event_message}'
                    )
            else:
                if event == 'all':
                    status = (
                        f'**{ctx.author.name}**, the alert message for **all** events was reset.\n'
                        f'The bot will use the default alert messages (see `{ctx.prefix}settings`).'
                    )
                else:
                    status = (
                        f'**{ctx.author.name}**, the alert message for {event} events was reset.\n'
                        f'The bot will use the default alert message (see `{ctx.prefix}settings`).'
                    )
        else:
            status = f'**{ctx.author.name}**, you have never used the bot on this server before. Please try again.'
    except sqlite3.Error as error:
        await log_error(ctx, error)

    return status

# Enable/disable specific event reminders
async def set_specific_event(ctx, event, action):

    if action == 'enable':
        enabled = 1
    elif action == 'disable':
        enabled = 0
    else:
        await log_error(ctx, f'Invalid action {action} in \'set_specific_event\'')
        if DEBUG_MODE == 'ON':
            status = 'Something went wrong here. Check the error log.'
        return

    column = ''

    if event == 'all':
        column = 'chop_enabled' # Pseudo value
    elif event == 'arena':
        column = 'arena_enabled'
    elif event == 'chop':
        column = 'chop_enabled'
    elif event == 'fish':
        column = 'fish_enabled'
    elif event == 'catch':
        column = 'catch_enabled'
    elif event == 'summon':
        event = 'lootbox summoning'
        column = 'summon_enabled'
    elif event == 'legendary-boss':
        event = 'legendary boss'
        column = 'boss_enabled'
    elif event == 'miniboss':
        column = 'miniboss_enabled'
    elif event == 'rumble-royale':
        column = 'rumble_enabled'

    else:
        await log_error(ctx, f'Invalid event {event} in \'set_specific_event\'')
        if DEBUG_MODE == 'ON':
            status = 'Something went wrong here. Check the error log.'
        return

    try:
        cur=erg_db.cursor()

        cur.execute(f'SELECT {column} FROM settings_guild WHERE guild_id=?', (ctx.guild.id,))
        record = cur.fetchone()

        if record:
            if not event == 'all':
                enabled_db = record[0]
                if enabled_db != enabled:
                    cur.execute(f'UPDATE settings_guild SET {column} = ? WHERE guild_id = ?', (enabled, ctx.guild.id,))
                    event = event.replace('-',' ')
                    status = f'**{ctx.author.name}**, {event} alerts are now **{action}d**.'
                else:
                    event = event.replace('-',' ')
                    status = f'**{ctx.author.name}**, {event} alerts are already **{action}d**.'
            else:
                cur.execute(f'UPDATE settings_guild SET arena_enabled = ?, boss_enabled = ?, catch_enabled = ?, chop_enabled = ?, fish_enabled = ?, miniboss_enabled = ?, summon_enabled = ?, rumble_enabled = ? WHERE guild_id = ?', (enabled, enabled, enabled, enabled, enabled, enabled, enabled, enabled, ctx.guild.id,))
                status = f'**{ctx.author.name}**, all event alerts are now **{action}d**.'
        else:
            status = f'**{ctx.author.name}**, you have never used the bot on this server before. Please try again.'
    except sqlite3.Error as error:
        await log_error(ctx, error)

    return status