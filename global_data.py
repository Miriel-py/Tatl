# global_data.py

import os
import emojis

# Get bot directory
bot_dir = os.path.dirname(__file__)

# Databases
dbfile = os.path.join(bot_dir, 'database/tatl_db.db')

# Donor tier reductions
donor_cooldowns = (1,0.9,0.8,0.65,)

# Prefix
default_prefix = 'tatl '

# Default messages
arena_message = f'Type **`JOIN`** to get {emojis.event_arena} cookies!'
boss_message = f'Type **`TIME TO FIGHT`** to defeat the {emojis.event_boss} boss!'
catch_message = f'Type **`CATCH`** to get {emojis.event_catch} coins!'
chop_message = f'Type **`CHOP`** to get {emojis.event_chop} logs!'
fish_message = f'Type **`FISH`** to get {emojis.event_fish} fish!'
miniboss_message = f'Type **`FIGHT`** to defeat the {emojis.event_miniboss} miniboss!'
summon_message = f'Type **`SUMMON`** to get a {emojis.event_summon} lootbox!'

# All events
events = ['all','arena','catch','chop','fish','legendary-boss','lootbox','miniboss',]
event_aliases = {
    'legendary': 'legendary-boss',
    'boss': 'legendary-boss',
    'legendaryboss': 'legendary-boss',
    'lb': 'lootbox',
    'summon': 'lootbox',
    'summoning': 'lootbox',
    'lbsummon': 'lootbox',
    'lbsummoning': 'lootbox',
    'lootboxsummon': 'lootbox',
    'lootboxsummoning': 'lootbox',
    'megalodon': 'fish',
    'bait': 'fish',
    'ultrabait': 'fish',
    'ultra-bait': 'fish',
    'river': 'fish',
    'tree': 'chop',
    'epictree': 'chop',
    'epic-tree': 'chop',
    'seed': 'chop',
    'epicseed': 'chop',
    'epic-seed': 'chop',
    'rain': 'catch',
    'coinrain': 'catch',
    'coin-rain': 'catch',
    'join': 'arena',
    'fight': 'miniboss',
    'mb': 'miniboss'
}

# Embed color
color = 0xFFE600

# Set default footer
footer = 'Ding ding ding!'

# Error log file
logfile = os.path.join(bot_dir, 'logs/discord.log')