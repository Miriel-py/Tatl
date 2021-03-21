# bot.py
import os
import discord
import sqlite3
import shutil
import asyncio
import global_data
import emojis
import logging
import logging.handlers
import itertools

from datetime import datetime, timedelta
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound

# Check if log file exists, if not, create empty one
logfile = global_data.logfile
if not os.path.isfile(logfile):
    open(logfile, 'a').close()

# Read the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEBUG_MODE = os.getenv('DEBUG_MODE')

# Initialize logger
logger = logging.getLogger('discord')
if DEBUG_MODE == 'ON':
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(filename=logfile,when='D',interval=1, encoding='utf-8', utc=True)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Set name of database files
dbfile = global_data.dbfile

# Open connection to the local database    
erg_db = sqlite3.connect(dbfile, isolation_level=None)

# Create task dictionary
running_tasks = {}

# Mixed Case prefix
async def mixedCase(*args):
  mixed_prefixes = []
  for string in args:
    all_prefixes = map(''.join, itertools.product(*((c.upper(), c.lower()) for c in string)))
    for prefix in list(all_prefixes):
        mixed_prefixes.append(prefix)

  return list(mixed_prefixes)

         
# --- Database: Get Data ---

# Check database for stored prefix, if none is found, a record is inserted and the default prefix - is used, return all bot prefixes
async def get_prefix_all(bot, ctx):
    
    try:
        cur=erg_db.cursor()
        cur.execute('SELECT prefix FROM settings_guild where guild_id=?', (ctx.guild.id,))
        record = cur.fetchone()
        
        if record:
            prefix_db = record[0].replace('"','')
            prefix_db_mixed_case = await mixedCase(prefix_db)
            prefixes = []
            for prefix in prefix_db_mixed_case:
                prefixes.append(prefix)
        else:
            prefix_mixed_case = await mixedCase(global_data.default_prefix)
            prefixes = []
            for prefix in prefix_mixed_case:
                prefixes.append(prefix)
            
            cur.execute('INSERT INTO settings_guild VALUES (?, ?)', (ctx.guild.id, global_data.default_prefix,))
    except sqlite3.Error as error:
        await log_error(ctx, error)
        
    return commands.when_mentioned_or(*prefixes)(bot, ctx)

# Check database for stored prefix, if none is found, the default prefix - is used, return only the prefix (returning the default prefix this is pretty pointless as the first command invoke already inserts the record)
async def get_prefix(ctx, guild_join=False):
    
    if guild_join == False:
        guild = ctx.guild
    else:
        guild = ctx
    
    try:
        cur=erg_db.cursor()
        cur.execute('SELECT prefix FROM settings_guild where guild_id=?', (guild.id,))
        record = cur.fetchone()
        
        if record:
            prefix = record[0]
        else:
            prefix = global_data.default_prefix
    except sqlite3.Error as error:
        if guild_join == False:
            await log_error(ctx, error)
        else:
            await log_error(ctx, error, True)
        
    return prefix
   
# Get dnd state from user id
async def get_dnd(user_id):

    try:
        cur=erg_db.cursor()
        cur.execute('SELECT dnd FROM settings_user where user_id=?', (user_id,))
        record = cur.fetchone()

        if record:
            setting_dnd = record[0]
    
    except sqlite3.Error as error:
        logger.error(f'Unable to get dnd mode setting: {error}')
  
    return setting_dnd
   
# Get settings
async def get_settings(ctx, event='all'):
    
    current_settings = None
    
    if event == 'all':
        sql = 'SELECT * FROM settings_guild where guild_id=?'
    elif event == 'arena':
        sql = 'SELECT arena_enabled, arena_role_id, arena_message FROM settings_guild where guild_id=?'
    elif event == 'legendary-boss':
        sql = 'SELECT boss_enabled, boss_role_id, boss_message FROM settings_guild where guild_id=?'
    elif event == 'catch':
        sql = 'SELECT catch_enabled, catch_role_id, catch_message FROM settings_guild where guild_id=?'
    elif event == 'chop':
        sql = 'SELECT chop_enabled, chop_role_id, chop_message FROM settings_guild where guild_id=?'
    elif event == 'fish':
        sql = 'SELECT fish_enabled, fish_role_id, fish_message FROM settings_guild where guild_id=?'
    elif event == 'miniboss':
        sql = 'SELECT miniboss_enabled, miniboss_role_id, miniboss_message FROM settings_guild where guild_id=?'
    elif event == 'lootbox':
        sql = 'SELECT summon_enabled, summon_role_id, summon_message FROM settings_guild where guild_id=?'
    
    try:
        cur=erg_db.cursor()
        cur.execute(sql, (ctx.guild.id,))
        record = cur.fetchone()
    
        if record:
            current_settings = record
    
    except sqlite3.Error as error:
        await log_error(ctx, error)    
  
    return current_settings



# --- Database: Write Data ---

# Set new prefix
async def set_prefix(bot, ctx, new_prefix):

    try:
        cur=erg_db.cursor()
        cur.execute('SELECT * FROM settings_guild where guild_id=?', (ctx.guild.id,))
        record = cur.fetchone()
        
        if record:
            cur.execute('UPDATE settings_guild SET prefix = ? where guild_id = ?', (new_prefix, ctx.guild.id,))           
        else:
            cur.execute('INSERT INTO settings_guild VALUES (?, ?)', (ctx.guild.id, new_prefix,))
    except sqlite3.Error as error:
        await log_error(ctx, error)

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
                    status = f'**{ctx.author.name}**, {event} alerts are now **{action}d**.'
                else:
                    status = f'**{ctx.author.name}**, {event} alerts are already **{action}d**.'
            else:
                cur.execute(f'UPDATE settings_guild SET arena_enabled = ?, boss_enabled = ?, catch_enabled = ?, chop_enabled = ?, fish_enabled = ?, miniboss_enabled = ?, summon_enabled = ? WHERE guild_id = ?', (enabled, enabled, enabled, enabled, enabled, enabled, enabled, ctx.guild.id,))
                status = f'**{ctx.author.name}**, all event alerts are now **{action}d**.'
        else:
            status = f'**{ctx.author.name}**, you have never used the bot on this server before. Please try again.'
    except sqlite3.Error as error:
        await log_error(ctx, error)
    
    return status



# --- Error Logging ---

# Error logging
async def log_error(ctx, error, guild_join=False):
    
    if guild_join == False:
        try:
            settings = ''
            try:
                guild_settings = await get_settings(ctx, 'all')
            except:
                settings = 'N/A'
            cur=erg_db.cursor()
            cur.execute('INSERT INTO errors VALUES (?, ?, ?, ?)', (ctx.message.created_at, ctx.message.content, str(error), settings))
        except sqlite3.Error as db_error:
            print(print(f'Error inserting error (ha) into database.\n{db_error}'))
    else:
        try:
            cur=erg_db.cursor()
            cur.execute('INSERT INTO errors VALUES (?, ?, ?, ?)', (datetime.now(), 'Error when joining a new guild', str(error), 'N/A'))
        except sqlite3.Error as db_error:
            print(print(f'Error inserting error (kek) into database.\n{db_error}'))



# --- Command Initialization ---
intents = discord.Intents().all()
bot = commands.Bot(command_prefix=get_prefix_all, help_command=None, case_insensitive=True, intents=intents)



# --- Ready & Join Events ---

# Set bot status when ready
@bot.event
async def on_ready():
    
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='your events'))
    
# Send message to system channel when joining a server
@bot.event
async def on_guild_join(guild):
    
    try:
        prefix = await get_prefix(guild, True)
        
        welcome_message = (
            f'Hey! **{guild.name}**! I\'m here to alert you when an Epic RPG event pops up!\n\n'
            f'Note that all alerts are off by default. Use `{prefix}help` to get started.\n'
            f'If you don\'t like this prefix, use `{prefix}setprefix` to change it.\n\n'
            f'Tip: If you ever forget the prefix, simply ping me with a command.'
        )
        
        await guild.system_channel.send(welcome_message)
    except:
        return



# --- Error Handling ---

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    elif isinstance(error, (commands.MissingPermissions)):
        missing_perms = ''
        for missing_perm in error.missing_perms:
            missing_perm = missing_perm.replace('_',' ').title()
            if not missing_perms == '':
                missing_perms = f'{missing_perms}, `{missing_perm}`'
            else:
                missing_perms = f'`{missing_perm}`'
        await ctx.reply(f'Sorry **{ctx.author.name}**, you need the permission(s) {missing_perms} to use this command.', mention_author=False)
    elif isinstance(error, (commands.BotMissingPermissions)):
        missing_perms = ''
        for missing_perm in error.missing_perms:
            missing_perm = missing_perm.replace('_',' ').title()
            if not missing_perms == '':
                missing_perms = f'{missing_perms}, `{missing_perm}`'
            else:
                missing_perms = f'`{missing_perm}`'
        await ctx.send(f'Sorry **{ctx.author.name}**, I\'m missing the permission(s) {missing_perms} to work properly.')
    elif isinstance(error, (commands.NotOwner)):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f'You\'re missing some arguments.', mention_author=False)
    else:
        await log_error(ctx, error) # To the database you go

       

# --- Main menu ---
# Main menu
@bot.command(aliases=('h',))
@commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
async def help(ctx):
    
    prefix = ctx.prefix
    if not prefix.lower() == 'rpg ':
        prefix = await get_prefix(ctx)
                    
        event_settings = (
            f'{emojis.bp} `{prefix}settings` : Show the current settings\n'
            f'{emojis.bp} `{prefix}enable` / `disable` : Enable/disable event alerts\n'
            f'{emojis.bp} `{prefix}role` : Set the roles to ping\n'
            f'{emojis.bp} `{prefix}message` : Set the messages the bot sends'
        )
        
        prefix_settings = (
            f'{emojis.bp} `{prefix}prefix` : Check the bot prefix\n'
            f'{emojis.bp} `{prefix}setprefix` / `{prefix}sp` : Set the bot prefix'
        )
        
        embed = discord.Embed(
            color = global_data.color,
            title = 'TATL',
            description = 'Ding ding ding!'
        )    
        embed.add_field(name='EVENT SETTINGS', value=event_settings, inline=False)
        embed.add_field(name='PREFIX SETTINGS', value=prefix_settings, inline=False)
        
        await ctx.reply(embed=embed, mention_author=False)



# --- Prefix Settings ---
   
# Command "setprefix" - Sets new prefix (if user has "manage server" permission)
@bot.command()
@commands.has_permissions(manage_guild=True)
@commands.bot_has_permissions(send_messages=True, read_message_history=True)
async def setprefix(ctx, *new_prefix):
    
    if not ctx.prefix == 'rpg ':
        if new_prefix:
            if len(new_prefix)>1:
                await ctx.reply(
                    f'The command syntax is `{ctx.prefix}setprefix [prefix]`.\n'
                    f'If you want to include a space in your prefix, use \" (example: `{ctx.prefix}setprefix "tatl "`)',
                    mention_author=False
                )
            else:
                await set_prefix(bot, ctx, new_prefix[0])
                await ctx.reply(f'Prefix changed to `{await get_prefix(ctx)}`.', mention_author=False)
        else:
            await ctx.reply(
                f'The command syntax is `{ctx.prefix}setprefix [prefix]`.\n'
                f'If you want to include a space in your prefix, use \" (example: `{ctx.prefix}setprefix "tatl "`)',
                mention_author=False
            )

# Command "prefix" - Returns current prefix
@bot.command()
@commands.bot_has_permissions(send_messages=True, read_message_history=True)
async def prefix(ctx):
    
    if not ctx.prefix == 'rpg ':
        current_prefix = await get_prefix(ctx)
        await ctx.reply(f'The prefix for this server is `{current_prefix}`\nTo change the prefix use `{current_prefix}setprefix`.', mention_author=False)



# --- Event Settings ---

# Command "settings" - Returns current event settings
@bot.command(aliases=('server','events','event','setting', 's'))
@commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
async def settings(ctx):
    
    prefix = ctx.prefix
    if not prefix.lower() == 'rpg ':
        settings = await get_settings(ctx, 'all')
        
        if settings == None:
            await ctx.reply(f'**{ctx.author.name}**, you have never used this bot before. Please try again.', mention_author=False)
            return
        else:
            
            arena_enabled = settings[2]
            arena_role_id = settings[3]
            arena_message = settings[4]
            boss_enabled = settings[5]
            boss_role_id = settings[6]
            boss_message = settings[7]
            catch_enabled = settings[8]
            catch_role_id = settings[9]
            catch_message = settings[10]
            chop_enabled = settings[11]
            chop_role_id = settings[12]
            chop_message = settings[13]
            fish_enabled = settings[14]
            fish_role_id = settings[15]
            fish_message = settings[16]
            miniboss_enabled = settings[17]
            miniboss_role_id = settings[18]
            miniboss_message = settings[19]
            summon_enabled = settings[20]
            summon_role_id = settings[21]
            summon_message = settings[22]
            
            events_enabled = [arena_enabled, boss_enabled, catch_enabled, chop_enabled, fish_enabled, miniboss_enabled, summon_enabled]
            event_roles = [arena_role_id, boss_role_id, catch_role_id, chop_role_id, fish_role_id, miniboss_role_id, summon_role_id]
                        
            for index in range(len(events_enabled)):
                event_enabled = events_enabled[index]
                if event_enabled == 1:
                    events_enabled[index] = 'Enabled'
                elif event_enabled == 0:
                    events_enabled[index] = 'Disabled'
            
            for index in range(len(event_roles)):
                event_role_id = event_roles[index]
                if event_role_id == 0:
                    event_roles[index] = '@here'
                elif event_role_id == ctx.guild.id:
                    event_roles[index] = ctx.guild.get_role(event_role_id).name
                else:
                    event_roles[index] = ctx.guild.get_role(event_role_id).mention
                    
            arena_enabled = events_enabled[0]
            arena_role = event_roles[0]
            boss_enabled = events_enabled[1]
            boss_role = event_roles[1]
            catch_enabled = events_enabled[2]
            catch_role = event_roles[2]
            chop_enabled = events_enabled[3]
            chop_role = event_roles[3]
            fish_enabled = events_enabled[4]
            fish_role = event_roles[4]
            miniboss_enabled = events_enabled[5]
            miniboss_role = event_roles[5]
            summon_enabled = events_enabled[6]
            summon_role = event_roles[6]
            
            if arena_message == None:
                arena_message = global_data.arena_message
            if boss_message == None:
                boss_message = global_data.boss_message
            if catch_message == None:
                catch_message = global_data.catch_message
            if chop_message == None:
                chop_message = global_data.chop_message
            if fish_message == None:
                fish_message = global_data.fish_message
            if miniboss_message == None:
                miniboss_message = global_data.miniboss_message
            if summon_message == None:
                summon_message = global_data.summon_message
        
            settings_arena = (
                f'{emojis.bp} Alerts: `{arena_enabled}`\n'
                f'{emojis.bp} Ping role: {arena_role}\n'
                f'{emojis.bp} Message: {arena_message}'
            )
            
            settings_boss = (
                f'{emojis.bp} Alerts: `{boss_enabled}`\n'
                f'{emojis.bp} Ping role: {boss_role}\n'
                f'{emojis.bp} Message: {boss_message}'
            )
            
            settings_catch = (
                f'{emojis.bp} Alerts: `{catch_enabled}`\n'
                f'{emojis.bp} Ping role: {catch_role}\n'
                f'{emojis.bp} Message: {catch_message}'
            )
            
            settings_chop = (
                f'{emojis.bp} Alerts: `{chop_enabled}`\n'
                f'{emojis.bp} Ping role: {chop_role}\n'
                f'{emojis.bp} Message: {chop_message}'
            )
            
            settings_fish = (
                f'{emojis.bp} Alerts: `{fish_enabled}`\n'
                f'{emojis.bp} Ping role: {fish_role}\n'
                f'{emojis.bp} Message: {fish_message}'
            )
            
            settings_miniboss = (
                f'{emojis.bp} Alerts: `{miniboss_enabled}`\n'
                f'{emojis.bp} Ping role: {miniboss_role}\n'
                f'{emojis.bp} Message: {miniboss_message}'
            )
            
            settings_summon = (
                f'{emojis.bp} Alerts: `{summon_enabled}`\n'
                f'{emojis.bp} Ping role: {summon_role}\n'
                f'{emojis.bp} Message: {summon_message}'
            )
        
            embed = discord.Embed(
                color = global_data.color,
                title = 'EVENT ALERT SETTINGS',
            )    
            embed.add_field(name='ARENA', value=settings_arena, inline=False)
            embed.add_field(name='CATCH (COIN RAIN)', value=settings_catch, inline=False)
            embed.add_field(name='CHOP (EPIC TREE)', value=settings_chop, inline=False)
            embed.add_field(name='FISH (MEGALODON)', value=settings_fish, inline=False)
            embed.add_field(name='LEGENDARY BOSS', value=settings_boss, inline=False)
            embed.add_field(name='LOOTBOX SUMMONING', value=settings_summon, inline=False)
            embed.add_field(name='MINIBOSS', value=settings_miniboss, inline=False)
        
            await ctx.reply(embed=embed, mention_author=False)

                         
# Command "enable/disable" - Enables/disables specific event alerts
@bot.command(aliases=('disable', 'e', 'd'))
@commands.has_permissions(manage_guild=True)
@commands.bot_has_permissions(send_messages=True, read_message_history=True)
async def enable(ctx, *args):
        
    event_list = 'Possible events:'
    for index in range(len(global_data.events)):
        event_list = f'{event_list}\n{emojis.bp} `{global_data.events[index]}`'
    
    if args:
        if len(args) == 1:
            event = args[0]
            event = event.lower()
            action = ctx.invoked_with
            if action == 'e':
                action = 'enable'
            if action == 'd':
                action = 'disable'

            if event in global_data.event_aliases:
                event = global_data.event_aliases[event]
            
            if event in global_data.events:
                status = await set_specific_event(ctx, event, action)
                await ctx.reply(status, mention_author=False)
            else:
                await ctx.reply(f'There is no event `{event}`.\n\n{event_list}', mention_author=False)
                return
        else:
            await ctx.reply(f'The syntax is `{ctx.prefix}{ctx.invoked_with} [event]`.\n\n{event_list}', mention_author=False)
            return
    else:
        await ctx.reply(f'The syntax is `{ctx.prefix}{ctx.invoked_with} [event]`.\n\n{event_list}', mention_author=False)
        return

# Command "role" - Sets/resets ping roles
@bot.command(aliases=('role', 'r'))
@commands.has_permissions(manage_guild=True)
@commands.bot_has_permissions(send_messages=True, read_message_history=True)
async def roles(ctx, *args):

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    event_list = 'Possible events:'
    for index in range(len(global_data.events)):
        event_list = f'{event_list}\n{emojis.bp} `{global_data.events[index]}`'

    if args:
        event = args[0]
        
        if event in global_data.event_aliases:
                event = global_data.event_aliases[event]
            
        if event in global_data.events:
            if len(args) == 2:
                role_or_action = args[1]
                
                if role_or_action in ('delete','reset','remove','off','disable'):
                    await ctx.reply(f'**{ctx.author.name}**, this will reset your event ping role(s). Are you sure? `[yes/no]`', mention_author=False)
                    try:
                        answer = await bot.wait_for('message', check=check, timeout=30)
                        if answer.content.lower() in ['yes','y']:
                            action = role_or_action
                            status = await set_event_role(ctx, 0, event)
                            await ctx.reply(status, mention_author=False)
                            return
                        else:
                            await ctx.send('Aborted.')
                    except asyncio.TimeoutError as error:
                        await ctx.send(f'**{ctx.author.name}**, you didn\'t answer in time.')
                else:
                    role_or_action = role_or_action
                    role_id = role_or_action.replace('<@&','').replace('>','')
                                
                    if role_id.isnumeric():
                        role_id = int(role_id)
                        role = ctx.guild.get_role(role_id)
                        if not role == None:
                            status = await set_event_role(ctx, role, event)
                            await ctx.reply(status, mention_author=False)
                            return
                        else:    
                            await ctx.reply(f'This is not a valid role. The syntax is `{ctx.prefix}{ctx.invoked_with} [event] [@role]`.\nIf you want to reset a role, use `{ctx.prefix}{ctx.invoked_with} [event] reset`\n\n{event_list}', mention_author=False)
                            return
                    elif role_id == '@everyone':
                        role_id = ctx.guild.id
                        role = ctx.guild.get_role(role_id)
                        if not role == None:
                            status = await set_event_role(ctx, role, event)
                            await ctx.reply(status, mention_author=False)
                            return
                        else:    
                            await ctx.reply(f'This is not a valid role. The syntax is `{ctx.prefix}{ctx.invoked_with} [event] [@role]`.\nIf you want to reset a role, use `{ctx.prefix}{ctx.invoked_with} [event] reset`\n\n{event_list}', mention_author=False)
                            return
                    else:
                        await ctx.reply(f'This is not a valid role. The syntax is `{ctx.prefix}{ctx.invoked_with} [event] [@role]`.\nIf you want to reset a role, use `{ctx.prefix}{ctx.invoked_with} [event] reset`\n\n{event_list}', mention_author=False)
                        return   
            else:
                await ctx.reply(f'The syntax is `{ctx.prefix}{ctx.invoked_with} [event] [@role]`.\nIf you want to reset a role, use `{ctx.prefix}{ctx.invoked_with} [event] reset`\n\n{event_list}', mention_author=False)
                return
        else:
            await ctx.reply(f'There is no event `{event}`.\n\n{event_list}', mention_author=False)
            return
    else:
                await ctx.reply(
                    f'This command sets role that is pinged when an event is detected.\n'
                    f'The syntax is `{ctx.prefix}{ctx.invoked_with} [event] [@role]`.\n'
                    f'If you want to reset a role, use `{ctx.prefix}{ctx.invoked_with} [event] reset`\n\n{event_list}',
                    mention_author=False
                )
                return                

# Command "message" - Sets/resets messages
@bot.command(aliases=('message', 'm'))
@commands.has_permissions(manage_guild=True)
@commands.bot_has_permissions(send_messages=True, read_message_history=True)
async def messages(ctx, *args):

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    event_list = 'Possible events:'
    for index in range(len(global_data.events)):
        event_list = f'{event_list}\n{emojis.bp} `{global_data.events[index]}`'

    if args:
        event = args[0]
        
        if event in global_data.event_aliases:
                event = global_data.event_aliases[event]
            
        if event in global_data.events:
            if len(args) > 1:
                action = args[1]
                if action in ('delete','reset','remove','off','disable'):
                    await ctx.reply(f'**{ctx.author.name}**, this will reset your event message(s). Are you sure? `[yes/no]`', mention_author=False)
                    try:
                        answer = await bot.wait_for('message', check=check, timeout=30)
                        if answer.content.lower() in ['yes','y']:
                            status = await set_event_message(ctx, None, event)
                            await ctx.reply(status, mention_author=False)
                            return
                        else:
                            await ctx.send('Aborted.')
                            return
                    except asyncio.TimeoutError as error:
                        await ctx.send(f'**{ctx.author.name}**, you didn\'t answer in time.')
                else:
                    await ctx.reply(f'**{ctx.author.name}**, please enter the alert message your want to set: (type `abort` to abort)', mention_author=False)
                    try:
                        answer = await bot.wait_for('message', check=check, timeout=30)
                        if not answer.content.lower() in ['abort','cancel']:
                            status = await set_event_message(ctx, answer.content, event)
                            await ctx.reply(status, mention_author=False)
                            return
                        else:
                            await ctx.send('Aborted.')
                            return
                    except asyncio.TimeoutError as error:
                        await ctx.send(f'**{ctx.author.name}**, you didn\'t answer in time.')
            else:
                await ctx.reply(f'**{ctx.author.name}**, please enter the alert message your want to set: (type `abort` to abort)', mention_author=False)
                try:
                    answer = await bot.wait_for('message', check=check, timeout=30)
                    if not answer.content.lower() in ['abort','cancel']:
                        status = await set_event_message(ctx, answer.content, event)
                        await ctx.reply(status, mention_author=False)
                        return
                    else:
                        await ctx.send('Aborted.')
                        return
                except asyncio.TimeoutError as error:
                    await ctx.send(f'**{ctx.author.name}**, you didn\'t answer in time.')
        else:
            await ctx.reply(f'There is no event `{event}`.\n\n{event_list}', mention_author=False)
            return
    else:
                await ctx.reply(
                    f'This command sets the message that is sent when an event is detected.\n'
                    f'The syntax is `{ctx.prefix}{ctx.invoked_with} [event]`.\n'
                    f'If you want to reset a role, use `{ctx.prefix}{ctx.invoked_with} [event] reset`\n\n{event_list}',
                    mention_author=False
                )
                return     



# --- Event alerts ---
# Event alerts
@bot.event
async def on_message(message):
    if message.author.id == 555955826880413696:
        if message.embeds:
            try:
                message_description = str(message.embeds[0].description)
                message_title = str(message.embeds[0].title)
                try:
                    message_fields = str(message.embeds[0].fields)
                except:
                    message_fields = ''
            except:
                return
            
            message_content = f'Description: {message_description}\nTitle: {message_title}\nFields: {message_fields}'
            logger.debug(f'Event detection: {message_content}')
            
            event = ''
            
            if message_content.find('IT\'S RAINING COINS') > -1:
                event = 'catch'
            elif message_content.find('AN EPIC TREE HAS JUST GROWN') > -1:
                event = 'chop'
            elif message_content.find('A MEGALODON HAS SPAWNED IN THE RIVER') > -1:
                event = 'fish'
            elif message_content.find('A LOOTBOX SUMMONING HAS STARTED') > -1:
                event = 'lootbox'
            elif message_content.find('A LEGENDARY BOSS JUST SPAWNED') > -1:
                event = 'legendary-boss'
            elif message_content.find('Type `join` to join the arena!') > -1:
                event = 'arena'
            elif message_content.find('Type `fight` to help and get a reward!') > -1:
                event = 'miniboss'
            
            if not event == '':
                event_settings = await get_settings(message, event)
                event_enabled = event_settings[0]
                event_role_id = event_settings[1]
                event_message = event_settings[2]
                
                if event_message == None:
                    if event == 'catch':
                        event_message = global_data.catch_message
                    elif event == 'chop':
                        event_message = global_data.chop_message
                    elif event == 'fish':
                        event_message = global_data.fish_message
                    elif event == 'lootbox':
                        event_message = global_data.summon_message
                    elif event == 'legendary-boss':
                        event_message = global_data.boss_message
                    elif event == 'arena':
                        event_message = global_data.arena_message
                    elif event == 'miniboss':
                        event_message = global_data.miniboss_message
                
                if event_enabled == 1:
                    if not event_role_id == 0:
                        role = message.guild.get_role(event_role_id)
                        await message.channel.send(f'{role.mention} {event_message}')
                    else:
                        await message.channel.send(f'@here {event_message}')
            
            await bot.process_commands(message)
    else:
        await bot.process_commands(message)


# --- Miscellaneous ---

# Statistics command
@bot.command(aliases=('statistic','statistics,','devstat','ping','about','info','stats'))
@commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
async def devstats(ctx):

    prefix = ctx.prefix
    if not prefix.lower() == 'rpg ':
        guilds = len(list(bot.guilds))
        latency = bot.latency
        
        embed = discord.Embed(
            color = global_data.color,
            title = f'BOT STATISTICS',
            description =   f'{emojis.bp} {guilds:,} servers\n'\
                            f'{emojis.bp} {round(latency*1000):,} ms latency'
        )
        
        await ctx.reply(embed=embed, mention_author=False) 


# --- Owner Commands ---

# Shutdown command (only I can use it obviously)
@bot.command()
@commands.is_owner()
@commands.bot_has_permissions(send_messages=True, read_message_history=True)
async def shutdown(ctx):

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    prefix = ctx.prefix
    if not prefix.lower() == 'rpg ':    
        try:
            await ctx.reply(f'**{ctx.author.name}**, are you **SURE**? `[yes/no]`', mention_author=False)
            answer = await bot.wait_for('message', check=check, timeout=30)
            if answer.content.lower() in ['yes','y']:
                await ctx.send(f'Shutting down.')
                await ctx.bot.logout()
            else:
                await ctx.send(f'Phew, was afraid there for a second.')
        except asyncio.TimeoutError as error:
            await ctx.send(f'**{ctx.author.name}**, you didn\'t answer in time.')

bot.run(TOKEN)