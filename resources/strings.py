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

ALERTS_ALL = ALERTS[:]
ALERTS_ALL.append('all')
ALERTS_ALL.sort()

# All events that have a role and message setting
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

ROLES_MESSAGES_ALL = ROLES_MESSAGES[:]
ROLES_MESSAGES_ALL.append('all')
ROLES_MESSAGES_ALL.sort()

# Key: Event name
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

# Key: Event name
# Value: Default message
DEFAULT_MESSAGES = {
    'arena': f'Type or click on **`JOIN`** to get {emojis.EVENT_ARENA} cookies!',
    'catch': f'Type or click on **`CATCH`** to get {emojis.EVENT_CATCH} coins!',
    'chop': f'Type or click on **`CHOP`** to get {emojis.EVENT_CHOP} logs!',
    'fish': f'Type or click on **`FISH`** to get {emojis.EVENT_FISH} fish!',
    'miniboss': f'Type or click on **`FIGHT`** to defeat the {emojis.EVENT_MINIBOSS} miniboss!',
    'legendary-boss': f'Type or click on **`TIME TO FIGHT`** to defeat the {emojis.EVENT_BOSS} boss!',
    'rumble-royale': f'Click on {emojis.EVENT_RUMBLE} to join the fight!',
    'summon': f'Type or click on **`SUMMON`** to get a {emojis.EVENT_SUMMON} lootbox!',
}

MSG_SYNTAX = 'The command syntax is `{syntax}`'

