# bot.py
import os
import discord
import sqlite3
import shutil
import asyncio

from datetime import datetime, timedelta

from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound

import database
from resources import settings


intents = discord.Intents.none()
intents.guilds = True   # for on_guild_join() and bot.guilds
intents.messages = True   # for literally everything the bot does


bot = commands.Bot(command_prefix=database.get_prefix_all, help_command=None, case_insensitive=True, intents=intents)


EXTENSIONS = [
    'cogs.auto_flex',
    'cogs.dev',
    'cogs.events',
    'cogs.main',
    'cogs.settings'
]
if __name__ == '__main__':
    for extension in EXTENSIONS:
        bot.load_extension(extension)


bot.run(settings.TOKEN)





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
            f'{emojis.bp} `{prefix}enable` / `disable` : Enable/disable alerts\n'
            f'{emojis.bp} `{prefix}event-role` : Set the event roles to ping\n'
            f'{emojis.bp} `{prefix}event-message` : Set the event messages the bot sends'
            f'{emojis.bp} `{prefix}flex-channel` : Set the auto flex channel'
        )

        auto_flex_settings = (
            f'{emojis.bp} `{prefix}flex on` / `off` : Enable/disable auto flex\n'
            f'{emojis.bp} `{prefix}flex channel set` / `reset` : Set/reset the auto flex channel\n'
        )

        prefix_settings = (
            f'{emojis.bp} `{prefix}prefix` : Check/set the bot prefix\n'
        )

        embed = discord.Embed(
            color = global_data.color,
            title = 'TATL',
            description = 'Ding ding ding!'
        )
        embed.add_field(name='EVENT SETTINGS', value=event_settings, inline=False)
        embed.add_field(name='PREFIX SETTINGS', value=prefix_settings, inline=False)

        await ctx.reply(embed=embed, mention_author=False)



# --- Event alerts ---
# Event alerts
@bot.event
async def on_message(message):
    if message.author.id in (555955826880413696,693167035068317736):
        if message.embeds:
            try:
                message_description = str(message.embeds[0].description)
            except:
                message_description = ''
            try:
                message_title = str(message.embeds[0].title)
            except:
                message_title = ''
            try:
                message_fields = str(message.embeds[0].fields)
            except:
                message_fields = ''
            try:
                message_footer = str(message.embeds[0].footer)
            except:
                message_footer = ''

            message_content = f'Description: {message_description}\nTitle: {message_title}\nFields: {message_fields}\nFooter {message_footer}'
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
            elif (message_content.find('Click the emoji below to join.') > -1) or (message_content.find('Click the emoji below to join!') > -1) or (message_content.find('Bet battle. Fee will automatically be deducted.') > -1):
                event = 'rumble-royale'

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
                    elif event == 'rumble-royale':
                        event_message = global_data.rumble_message

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
    """Shows some bot info"""
    start_time = datetime.utcnow()
    message = await ctx.send('Testing API latency...')
    end_time = datetime.utcnow()
    elapsed_time = end_time - start_time
    bot_status = (
        f'{emojis.bp} {len(bot.guilds):,} servers\n'
        f'{emojis.bp} Bot latency: {round(bot.latency*1000):,} ms\n'
        f'{emojis.bp} API latency: {round(elapsed_time.total_seconds()*1000):,} ms'
        )
    creator = f'{emojis.bp} Miriel#0001'
    embed = discord.Embed(color = global_data.color, title = 'ABOUT TATL')
    embed.add_field(name='BOT STATS', value=bot_status, inline=False)
    embed.add_field(name='CREATOR', value=creator, inline=False)
    await message.edit(content=None, embed=embed)


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

