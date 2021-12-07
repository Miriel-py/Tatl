# events.py
"""Contains the on_message handling for event alerts"""

import discord
from discord.ext import commands

import database
from resources import emojis, settings


class EventsCog(commands.Cog):
    """Cog with on_message event"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Runs when a message is sent in a channel."""
        if message.author.id == settings.EPIC_RPG_ID and not message.embeds:
            message_content = message.content
            laugh_terms = [
                'You just lost your lootbox',
                'fighting them wasn\'t very clever',
                'took the seed from the ground and decided to try planting it again later',
                'While trying to enchant your broken sword again',
                'What?? Get in the car',
                'died fighting the **mysterious man**'
            ]
            if ('For some completely unknown reason, the following pets are back instantly' in message_content
                or 'IT CAME BACK INSTANTLY!!' in message_content):
                await message.add_reaction(emojis.SKILL_TIME_TRAVELER)
                return
            elif 'CHRISTMAS SLIME' in message_content and 'got 100' in message_content:
                await message.add_reaction(emojis.XMAS_YAY)
                return
            elif any(term in message_content for term in laugh_terms):
                await message.add_reaction(emojis.PEPE_LAUGH)
                return

        if message.author.id in (settings.EPIC_RPG_ID,settings.RUMBLE_ROYALE_ID) and message.embeds:
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
            message_content = (
                f'Description: {message_description}\n'
                f'Title: {message_title}\n'
                f'Fields: {message_fields}\n'
                f'Footer {message_footer}'
            )

            event = ''
            if 'IT\'S RAINING COINS' in message_content:
                event = 'catch'
            elif 'AN EPIC TREE HAS JUST GROWN' in message_content:
                event = 'chop'
            elif 'A MEGALODON HAS SPAWNED IN THE RIVER' in message_content:
                event = 'fish'
            elif 'A LOOTBOX SUMMONING HAS STARTED' in message_content:
                event = 'summon'
            elif 'A LEGENDARY BOSS JUST SPAWNED' in message_content:
                event = 'boss'
            elif 'Type `join` to join the arena!' in message_content:
                event = 'arena'
            elif 'Type `fight` to help and get a reward!' in message_content:
                event = 'miniboss'
            elif ('Click the emoji below to join.' in message_content
                or 'Click the emoji below to join!' in message_content
                or 'Bet battle. Fee will automatically be deducted.' in message_content):
                event = 'rumble'

            # Halloween boss
            elif '**THE PUMPKIN BAT** IS ATTACKING YOU FROM BEHIND!' in message_content:
                await message.channel.send('`DODGE`')
                return
            elif '**THE PUMPKIN BAT** IS ATTACKING YOU FROM THE LEFT!' in message_content:
                await message.channel.send('`PUMPKIN`')
                return
            elif '**THE PUMPKIN BAT** IS ATTACKING YOU FROM THE RIGHT!' in message_content:
                await message.channel.send('`T POSE`')
                return
            elif '**THE PUMPKIN BAT** IS ATTACKING YOU AHEAD!' in message_content:
                await message.channel.send('`APPLE`')
                return

            # Temporary reactions, move to Navi later
            elif '** got bored and left' in message_content:
                await message.add_reaction(emojis.PANDA_SAD)
                return
            elif 'The legendary boss has not been defeated' in message_content:
                await message.add_reaction(emojis.PEPE_LAUGH)
                return
            elif 'welp, i guess no one wants my items' in message_content:
                await message.add_reaction(emojis.AWKWARD)
                return
            elif 'Everyone got 1' in message_content and 'common lootbox' in message_content:
                await message.add_reaction(emojis.PEPE_LAUGH)
                return
            elif ('common lootbox opened' in message_content and 'wooden log' in message_content
                  and '+1' in message_content and message_content.count('<:') == 2):
                await message.add_reaction(emojis.PEPE_LAUGH)
                return
            elif ('common lootbox opened' in message_content and 'normie fish' in message_content
                  and '+1' in message_content and message_content.count('<:') == 2):
                await message.add_reaction(emojis.PEPE_LAUGH)
                return

            if not event == '':
                guild_settings: database.Guild = await database.get_guild(message.guild)
                event_settings: database.GuildEvent = getattr(guild_settings, event)
                if event_settings.enabled:
                    if not event_settings.role_id == 0:
                        role = message.guild.get_role(event_settings.role_id)
                        await message.channel.send(f'{role.mention} {event_settings.message}')
                    else:
                        await message.channel.send(f'@here {event_settings.message}')


# Initialization
def setup(bot):
    bot.add_cog(EventsCog(bot))