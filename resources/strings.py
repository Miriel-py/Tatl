# strings.py
"""Contains global strings"""

from resources import emojis


# All alerts that can be enabled/disabled
ALERTS = [
    'arena',
    'auto-flex',
    'catch',
    'chop',
    'fish',
    'legendary-boss',
    'miniboss',
    'rumble-royale',
    'summon'
]

# All alerts that have a role and message setting
ROLES_MESSAGES = [
    'arena',
    'catch',
    'chop',
    'fish',
    'legendary-boss',
    'miniboss',
    'rumble-royale',
    'summon'
]

# Key: Alias
# Value: Alert name
ALERT_ALIASES = {
    'legendary': 'legendary-boss',
    'boss': 'legendary-boss',
    'legendaryboss': 'legendary-boss',
    'lb': 'summon',
    'lootbox': 'summon',
    'summoning': 'summon',
    'lbsummon': 'summon',
    'lbsummoning': 'summon',
    'lootboxsummon': 'summon',
    'lootboxsummoning': 'summon',
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
    'mb': 'miniboss',
    'rr': 'rumble-royale',
    'hg': 'rumble-royale',
    'rumble': 'rumble-royale',
    'royale': 'rumble-royale',
    'flex': 'auto-flex',
    'autoflex': 'auto-flex'
}

# Key: Alert name
# Value: Beginning of the column name in the database
ALERT_COLUMNS = {
    'arena': 'arena',
    'auto-flex': 'auto_flex',
    'catch': 'catch',
    'chop': 'chop',
    'fish': 'fish',
    'legendary-boss': 'boss',
    'miniboss': 'miniboss',
    'rumble-royale': 'rumble',
    'summon': 'summon',
}

DEFAULT_MSG_ARENA = f'Type **`JOIN`** to get {emojis.EVENT_ARENA} cookies!'
DEFAULT_MSG_BOSS = f'Type **`TIME TO FIGHT`** to defeat the {emojis.EVENT_BOSS} boss!'
DEFAULT_MSG_CATCH = f'Type **`CATCH`** to get {emojis.EVENT_CATCH} coins!'
DEFAULT_MSG_CHOP = f'Type **`CHOP`** to get {emojis.EVENT_CHOP} logs!'
DEFAULT_MSG_FISH = f'Type **`FISH`** to get {emojis.EVENT_FISH} fish!'
DEFAULT_MSG_MINIBOSS = f'Type **`FIGHT`** to defeat the {emojis.EVENT_MINIBOSS} miniboss!'
DEFAULT_MSG_SUMMON = f'Type **`SUMMON`** to get a {emojis.EVENT_SUMMON} lootbox!'
DEFAULT_MSG_RUMBLE = f'Click {emojis.EVENT_RUMBLE} to join the fight!'

MSG_SYNTAX = 'The command syntax is `{syntax}`'

