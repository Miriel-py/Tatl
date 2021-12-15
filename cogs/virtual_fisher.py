# virtual_fisher.py
"""Contains the on_message handling for virtial fisher alerts"""

import discord
from discord.ext import commands

import database
from resources import emojis, settings


class VirtualFisherCog(commands.Cog):
    """Cog with on_message event"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Runs when a message is sent in a channel."""
        if message.author.id == settings.VIRTUAL_FISHER_ID:
            if not message.embeds:
                message_content = message.content
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
                message_content = (
                    f'Description: {message_description}\n'
                    f'Title: {message_title}\n'
                    f'Fields: {message_fields}\n'
                    f'Footer {message_footer}'
                )

            fish_boost_ended = False
            treasure_boost_ended = False
            worker_ended = False
            personal_booster_ended = False
            bait_ended = False

            if 'Your fishing boost ended!' in message_content:
                fish_boost_ended = True
            if 'Your treasure boost ended!' in message_content:
                treasure_boost_ended = True
            if 'Your worker has stopped working' in message_content:
                worker_ended = True
            if 'Your personal booster ended!' in message_content:
                personal_booster_ended = True
            if 'You ran out of' in message_content:
                bait_ended = True

            answer = ''
            if fish_boost_ended:
                answer = f'{answer}\nYour fishing boost ended!'
            if treasure_boost_ended:
                answer = f'{answer}\nYour treasure boost ended!'
            if worker_ended:
                answer = f'{answer}\nYour worker has stopped working!'
            if personal_booster_ended:
                answer = f'{answer}\nYour personal booster ended!'
            if bait_ended:
                answer = f'{answer}\nYou ran out of bait!'


            if answer != '':
                await message.channel.send(answer.strip())


# Initialization
def setup(bot):
    bot.add_cog(VirtualFisherCog(bot))