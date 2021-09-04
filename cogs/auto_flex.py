# events.py
"""Contains the on_message handling for auto flex alerts"""

from logging import log
import discord
from discord import emoji
from discord.ext import commands

import database
from resources import emojis, logs, settings, strings


class AutoFlexCog(commands.Cog):
    """Cog with on_message event"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Events
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Runs when a message is sent in a channel."""
        if message.author.id in (settings.EPIC_RPG_ID, 619879176316649482):
            if not message.embeds:
                message_content = message.content
            else:
                try:
                    message_author = str(message.embeds[0].author)
                except:
                    message_author = ''
                try:
                    message_title = str(message.embeds[0].title)
                except:
                    message_title = ''
                try:
                    message_description = str(message.embeds[0].description)
                except:
                    message_description = ''
                try:
                    message_fields = str(message.embeds[0].fields)
                except:
                    message_fields = ''
                try:
                    message_footer = str(message.embeds[0].footer)
                except:
                    message_footer = ''
                message_content = (
                    f'Author: {message_author}\n'
                    f'Title: {message_title}\n'
                    f'Description: {message_description}\n'
                    f'Fields: {message_fields}\n'
                    f'Footer {message_footer}'
                )

            event = ''
            if 'is this a **dream**????' in message_content.lower():
                event = 'work_ultra'
                logs.logger.info(message_content)
            elif 'pet adventure rewards' in message_content.lower() and 'ultra log' in message_content.lower():
                event = 'pet_ultra'
                logs.logger.info(message_content)
            elif 'this pet has obtained the **ascended** skill' in message_content.lower():
                event = 'pet_ascend'
                logs.logger.info(message_content)
            elif 'the melting heat required to forge this sword was so much' in message_content.lower():
                event = 'forge_godly'
                logs.logger.info(message_content)
            elif 'lootbox opened! (x100)' in message_content.lower():
                event = 'lb_100'
                logs.logger.info(message_content)
            elif (('found and killed' in message_content.lower() or 'are hunting together' in message_content.lower())
                  and 'omega lootbox' in message_content.lower()):
                event = 'lb_omega'
                logs.logger.info(message_content)
            elif (('found and killed' in message_content.lower() or 'are hunting together' in message_content.lower())
                  and 'godly lootbox' in message_content.lower()):
                event = 'lb_godly'
                logs.logger.info(message_content)
            elif 'edgy lootbox opened!' in message_content.lower() and 'ultra log' in message_content.lower():
                event = 'lb_edgy_ultra'
                logs.logger.info(message_content)
            elif 'omega lootbox opened!' in message_content.lower() and 'ultra log' in message_content.lower():
                event = 'lb_omega_ultra'
                logs.logger.info(message_content)
            elif 'has unlocked the **ascended skill**' in message_content.lower():
                event = 'pr_ascension'
                logs.logger.info(message_content)
            elif 'has traveled in time' in message_content.lower():
                event = 'pr_timetravel'
                logs.logger.info(message_content)
            elif "'s enchant" in message_content.lower():
                enchants = ['edgy','ultra-edgy','omega','ultra-omega','godly']
                if any(enchant in message_content.lower() for enchant in enchants):
                    event = 'enchant_enchant'
                    logs.logger.info(message_content)
            elif "'s refine" in message_content.lower():
                enchants = ['ultra-edgy','omega','ultra-omega','godly']
                if any(enchant in message_content.lower() for enchant in enchants):
                    event = 'enchant_refine'
                    logs.logger.info(message_content)
            elif "'s transmute" in message_content.lower():
                enchants = ['omega','ultra-omega','godly']
                if any(enchant in message_content.lower() for enchant in enchants):
                    event = 'enchant_transmute'
                    logs.logger.info(message_content)
            elif "'s transcend" in message_content.lower():
                enchants = ['ultra-omega','godly']
                if any(enchant in message_content.lower() for enchant in enchants):
                    event = 'enchant_transcend'
                    logs.logger.info(message_content)
            elif "wait what? it landed on its side" in message_content.lower():
                event = 'gambling_coinflip'
                logs.logger.info(message_content)
            elif "'s slots" in message_content.lower():
                icons = ['💎','💯','🎁','✨','🍀']
                if any(message_content.lower().count(icon) == 5 for icon in icons):
                    event = 'gambling_slots'
                    logs.logger.info(message_content)
            elif 'accumulated failed attempts: 0' in message_content.lower():
                event = 'horse_tier'
                logs.logger.info(message_content)
            elif 'the legendary boss died! everyone leveled up' in message_content.lower():
                event = 'event_boss'
                logs.logger.info(message_content)
            elif 'your lootbox has evolved to an omega lootbox' in message_content.lower():
                event = 'event_lb'
                logs.logger.info(message_content)
            elif ('your sword got an ultra-edgy enchantment' in message_content.lower()
                  or 'your armor got an ultra-edgy enchantment' in message_content.lower()):
                event = 'event_enchant'
                logs.logger.info(message_content)
            elif 'the seed surrendered' in message_content.lower():
                event = 'event_farm'
                logs.logger.info(message_content)
            elif 'killed the mysterious man' in message_content.lower():
                event = 'event_heal'
                logs.logger.info(message_content)
            elif 'killed the **epic guard**' in message_content.lower():
                event = 'event_jail'
                logs.logger.info(message_content)

            if not event == '':
                guild_settings = database.Guild
                guild_settings = await database.get_guild(message.guild)
                if guild_settings.auto_flex_enabled and guild_settings.auto_flex_channel_id != 0:
                    await self.bot.wait_until_ready()
                    auto_flex_channel = self.bot.get_channel(guild_settings.auto_flex_channel_id)
                    embed = await embed_auto_flex(message, message_content, event)
                    await auto_flex_channel.send(embed=embed)


# Initialization
def setup(bot):
    bot.add_cog(AutoFlexCog(bot))


# Embeds
async def embed_auto_flex(message: discord.Message, message_content:str, event: str) -> discord.Embed:
    """Auto flex embed"""

    flex_titles = {
        'work_ultra': f'{emojis.LOG_ULTRA} It\'s not a dream!',
        'pet_ultra': f'{emojis.LOG_ULTRA} ULTRA l...azy',
        'pet_ascend': f'{emojis.SKILL_ASCENDED} No skill champ',
        'forge_godly': f'{emojis.SWORD_GODLY} Almost a cookie',
        'lb_100': f'{emojis.SLOTS_100} Look at that pile!',
        'lb_omega': f'{emojis.LB_OMEGA} OH MEGA!',
        'lb_godly': f'{emojis.LB_GODLY} WAIT WHAT?',
        'lb_edgy_ultra': f'{emojis.LOG_ULTRA} It\'s just an EDGY, lol',
        'lb_omega_ultra': f'{emojis.LOG_ULTRA} That\'s a lot of wood',
        'pr_ascension': f'{emojis.ASCENSION} Up up and away',
        'pr_timetravel': f'{emojis.TIME_TRAVEL} Allons-y!',
        'enchant_enchant': f'{emojis.ENCHANTMENT} Simply enchanting!',
        'enchant_refine': f'{emojis.ENCHANTMENT} Refine has a higher chance... they said',
        'enchant_transmute': f'{emojis.ENCHANTMENT} Transmutant',
        'enchant_transcend': f'{emojis.ENCHANTMENT} Lost in Transcendation',
        'gambling_coinflip': f'{emojis.COIN} Stop gambling, kids!',
        'gambling_slots': f'{emojis.SLOTS_CLOVER} JACKPOT',
        'horse_tier': f'{emojis.HORSE_T1} Horseback Mountain',
        'event_boss': f'{emojis.EVENT_BOSS} LEGEN... WAIT FOR IT... (seriously, wait for it, gonna be a while)',
        'event_lb': f'{emojis.LB_OMEGA} They did what now?',
        'event_enchant': f'{emojis.BOOM} Twice the fun',
        'event_farm': f'{emojis.CROSSED_SWORDS} Totally believable level up story',
        'event_heal': f'{emojis.LIFE_POTION} Very mysterious',
        'event_jail': f'{emojis.EPIC_GUARD} But... why?',
    }

    flex_description_functions = {
        'work_ultra': get_work_ultra_description,
        'pet_ultra': get_pet_ultra_description,
        'pet_ascend': get_pet_ascend_description,
        'forge_godly': get_forge_godly_description,
        'lb_100': get_lb_100_description,
        'lb_omega': get_lb_omega_description,
        'lb_godly': get_lb_godly_description,
        'lb_edgy_ultra': get_lb_edgy_ultra_description,
        'lb_omega_ultra': get_lb_omega_ultra_description,
        'pr_ascension': get_pr_ascension_description,
        'pr_timetravel': get_pr_timetravel_description,
        'enchant_enchant': get_enchant_enchant_description,
        'enchant_refine': get_enchant_refine_description,
        'enchant_transmute': get_enchant_transmute_description,
        'enchant_transcend': get_enchant_transcend_description,
        'gambling_coinflip': get_gambling_coinflip_description,
        'gambling_slots': get_gambling_slots_description,
        'horse_tier': get_horse_tier_description,
        'event_boss': get_event_boss_description,
        'event_lb': get_event_lb_description,
        'event_enchant': get_event_enchant_description,
        'event_farm': get_event_farm_description,
        'event_heal': get_event_heal_description,
        'event_jail': get_event_jail_description,
    }

    flex_thumbnails = {
        'work_ultra': 'https://c.tenor.com/4ReodhBihBQAAAAC/ruthe-biber.gif',
        'pet_ultra': 'https://c.tenor.com/2HYVY5cyMAAAAAAC/pls-send-help-help-me.gif',
        'pet_ascend': 'https://c.tenor.com/yyiGOtquk74AAAAC/rocket-clicks-rocket.gif',
        'forge_godly': 'https://c.tenor.com/OSYJN4DF0tEAAAAC/light-up.gif',
        'lb_100': 'https://c.tenor.com/KEky01zvXLMAAAAC/we-bare-bears-grizzly.gif',
        'lb_omega': 'https://c.tenor.com/0ZYUSU6NtMkAAAAC/box-cartoon-box.gif',
        'lb_godly': 'https://c.tenor.com/U3I7KkH0w50AAAAC/unbeliavable-inconceivable.gif',
        'lb_edgy_ultra': 'https://c.tenor.com/clnoM8TeSxcAAAAC/wait-what-unbelievable.gif',
        'lb_omega_ultra': 'https://c.tenor.com/Dm7vWLpdTpcAAAAC/seinfeld.gif',
        'pr_ascension': 'https://c.tenor.com/Jpx1xCUOyz8AAAAC/ascend.gif',
        'pr_timetravel': 'https://c.tenor.com/bI5cZAs6klMAAAAC/11th-doctor-doctor-who.gif',
        'enchant_enchant': 'https://c.tenor.com/0LZHWJz6lLIAAAAC/sword-in-the-stone-excalibur.gif',
        'enchant_refine': 'https://c.tenor.com/-08JLwayFF8AAAAC/sword-inuyasha.gif',
        'enchant_transmute': 'https://c.tenor.com/AvGZ4QEw6xUAAAAC/sword.gif',
        'enchant_transcend': 'https://c.tenor.com/9-b0gUv-HokAAAAC/enchanted-sword-enchanted-iron-sword.gif',
        'gambling_coinflip': 'https://c.tenor.com/GtTxw8NRrlwAAAAC/dbh-connor.gif',
        'gambling_slots': 'https://c.tenor.com/vh6UO80RFmYAAAAC/toilet-paper-slot-machine.gif',
        'horse_tier': 'https://c.tenor.com/FMdPKbgHXbsAAAAC/horse-laugh.gif',
        'event_boss': 'https://c.tenor.com/ARAF0r6nJQAAAAAC/dragon-rawr.gif',
        'event_lb': 'https://c.tenor.com/6WfJrQYFXlYAAAAC/magic-kazaam.gif',
        'event_enchant': 'https://c.tenor.com/gAuPzxRCVw8AAAAC/link-dancing.gif',
        'event_farm': 'https://c.tenor.com/OEIwT0KEyREAAAAC/homer-fist.gif',
        'event_heal': 'https://c.tenor.com/IfAs08au8IYAAAAd/he-died-in-mysterious-circumstances-the-history-guy.gif',
        'event_jail': 'https://c.tenor.com/txj6Fp2ipqMAAAAC/prison-jail.gif',
    }

    embed_title = flex_titles[event]
    embed_description = await flex_description_functions[event](message_content)

    embed = discord.Embed(
        color = settings.EMBED_COLOR,
        title = embed_title,
        description = f'{embed_description}\n\n[Check it out]({message.jump_url})'
    )

    embed.set_thumbnail(url=flex_thumbnails[event])

    return embed


# Functions
async def get_work_ultra_description(message_content: str) -> str:
    """Returns the embed description for the work_ultra event"""
    user_name_string = '????? **'
    user_name_start = message_content.find(user_name_string) + len(user_name_string)
    user_name_end = message_content.find('** got', user_name_start)
    user_name = message_content[user_name_start:user_name_end]

    log_amount_string = '** got '
    log_amount_start = user_name_end + len(log_amount_string)
    log_amount_end = message_content.find(' <', log_amount_start)
    log_amount = message_content[log_amount_start:log_amount_end].strip()

    description = (
        f'**{user_name}** just found {log_amount} {emojis.LOG_ULTRA} ULTRA logs while "working".\n\n'
        f'And by "working" they apparently mean "having a mental breakdown".\n'
        f'Why else would they put a chainsaw in their mouth.'
    )

    return description


async def get_pet_ultra_description(message_content: str) -> str:
    """Returns the embed description for the pet_ultra event"""
    user_name_end = message_content.find("'s pets")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    log_amount_total = 0
    log_amount_string = ' <:ULTRA'
    log_amount_search_start = 0
    for ultralog in range(0, message_content.count(log_amount_string)):
        log_amount_end = message_content.find(log_amount_string, log_amount_search_start)
        log_amount_start = message_content.rfind("'", 0, log_amount_end) + 1
        log_amount = message_content[log_amount_start:log_amount_end]
        try:
            log_amount_total += int(log_amount.strip())
        except Exception as error:
            await database.log_error(f'Error: {error}\nFunction: get_pet_ultra_description\nlog_amount: {log_amount}')
            return
        log_amount_search_start = log_amount_end + len(log_amount_string)

    description = (
        f'**{user_name}** got {log_amount_total} {emojis.LOG_ULTRA} ULTRA logs by doing nothing at all and letting their '
        f'pets do all the work.\n\n'
        f'STOP PET SLAVERY!'
    )

    return description


async def get_pet_ascend_description(message_content: str) -> str:
    """Returns the embed description for the pet_ascend event"""
    user_name_string = "skill\n"
    user_name_start = message_content.find(user_name_string) + len(user_name_string) + 2
    user_name_end = message_content.find('** earned', user_name_start)
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** just ascended a pet!\n\n'
        f'To get more pets!\n\n'
        f'I mean... it sure feels great to destroy all of your skills for that!\n\n'
        f'...right?'
    )

    return description


async def get_forge_godly_description(message_content: str) -> str:
    """Returns the embed description for the forge_godly event"""
    user_name_string = 'exhausted'
    user_name_start = message_content.find(user_name_string) + len(user_name_string) + 1
    user_name_end = message_content.find(' earned', user_name_start)
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** forged a GODLY sword!\n\n'
        f'Wowzers, what an amazing thing!\n\n'
        f'Oh wait. It has 0 AT, lol.'
    )

    return description


async def get_lb_100_description(message_content: str) -> str:
    """Returns the embed description for the forge_godly event"""
    lootbox_type_emoji = {
        'common': emojis.LB_COMMON,
        'uncommon': emojis.LB_UNCOMMON,
        'rare': emojis.LB_RARE,
        'epic': emojis.LB_RARE,
        'edgy': emojis.LB_EDGY,
        'omega': emojis.LB_OMEGA,
        'godly': emojis.LB_GODLY
    }

    user_name_end = message_content.find("'s lootbox")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    lootbox_type_end = message_content.find(' lootbox opened!')
    lootbox_type_start = message_content.rfind(' ', 0, lootbox_type_end) + 1
    lootbox_type = message_content[lootbox_type_start:lootbox_type_end]

    try:
        lootbox_emoji = lootbox_type_emoji[lootbox_type.lower()]
    except Exception as error:
        await database.log_error(f'Error: {error}\nFunction: get_lb_100_description\nlootbox_type: {lootbox_type}')
        return

    description = (
        f'**{user_name}** managed to ~~hoard~~ open 100 {lootbox_emoji} {lootbox_type} lootboxes at once.\n\n'
        f'What a ~~hoarder~~ dedicated fellow!'
    )

    return description


async def get_lb_omega_description(message_content: str) -> str:
    """Returns the embed description for the lb_omega event"""
    hunt_together = True if 'are hunting together' in message_content else False

    if hunt_together:
        user_name_end = message_content.find("** and **")
    else:
        user_name_end = message_content.find("** found and killed")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    lootbox_amount_end = message_content.find(' <:OMEGA')
    lootbox_amount_start_search = 'got '
    lootbox_amount_start = message_content.rfind(lootbox_amount_start_search, 0, lootbox_amount_end) + len(lootbox_amount_start_search)
    lootbox_amount = message_content[lootbox_amount_start:lootbox_amount_end]
    try:
        lootbox_amount = int(lootbox_amount.strip())
    except Exception as error:
        await database.log_error(f'Error: {error}\nFunction: get_lb_omega_description\nlootbox_amount: {lootbox_amount}')
        return

    description = (
        f'**{user_name}** just found {lootbox_amount} {emojis.LB_OMEGA} OMEGA lootbox!\n\n'
        f'If you\'re not Ray: CONGRATULATIONS!\n'
        f'If you\'re Ray: Stop spamming this channel {emojis.CAT_GUN}'
    )

    return description


async def get_lb_godly_description(message_content: str) -> str:
    """Returns the embed description for the lb_godly event"""
    hunt_together = True if 'are hunting together' in message_content else False

    if hunt_together:
        user_name_end = message_content.find("** and **")
    else:
        user_name_end = message_content.find("** found and killed")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    lootbox_amount_end = message_content.find(' <:GODLY')
    lootbox_amount_string = 'got '
    lootbox_amount_start = message_content.rfind(lootbox_amount_string, 0, lootbox_amount_end) + len(lootbox_amount_string)
    lootbox_amount = message_content[lootbox_amount_start:lootbox_amount_end]
    try:
        lootbox_amount = int(lootbox_amount.strip())
    except Exception as error:
        await database.log_error(f'Error: {error}\nFunction: get_lb_godly_description\nlootbox_amount: {lootbox_amount}')
        return

    description = (
        f'**{user_name}** just found {lootbox_amount} {emojis.LB_GODLY} GODLY lootbox??!\n\n'
        f'I\'m pretty sure this is illegal und should be reported.'
    )

    return description


async def get_lb_edgy_ultra_description(message_content: str) -> str:
    """Returns the embed description for the lb_edgy_ultra event"""
    user_name_end = message_content.find("'s lootbox")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    log_amount_end = message_content.find(' <:ULTRA')
    log_amount_start = message_content.rfind('+', 0, log_amount_end) + 1
    log_amount = message_content[log_amount_start:log_amount_end]
    try:
        lootbox_amount = int(log_amount.strip())
    except Exception as error:
        await database.log_error(
            f'Error: {error}\nFunction: get_lb_edgy_ultra_description\nlog_amount: {log_amount}'
        )
        return

    description = (
        f'Look at **{user_name}**, opening that {emojis.LB_EDGY} EDGY lootbox like it\'s worth something, haha.\n\n'
        f'See. All he got is {log_amount} lousy {emojis.LOG_ULTRA} ULTRA log.\n\n'
        f'...\n\n'
        f'**How.**'
    )

    return description


async def get_lb_omega_ultra_description(message_content: str) -> str:
    """Returns the embed description for the lb_omega_ultra event"""
    user_name_end = message_content.find("'s lootbox")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    log_amount_end = message_content.find(' <:ULTRA')
    log_amount_start = message_content.rfind('+', 0, log_amount_end) + 1
    log_amount = message_content[log_amount_start:log_amount_end]
    try:
        lootbox_amount = int(log_amount.strip())
    except Exception as error:
        await database.log_error(
            f'Error: {error}\nFunction: get_lb_omega_ultra_description\nlog_amount: {log_amount}'
        )
        return

    description = (
        f'**{user_name}** opened an {emojis.LB_OMEGA} OMEGA lootbox!\n\n'
        f'And found {log_amount} {emojis.LOG_ULTRA} ULTRA log in there on top!\n\n'
        f'Tbh they probably stole that box from the server owner.\n'
        f'Something should arrest them, this is criminal.'
    )

    return description


async def get_pr_ascension_description(message_content: str) -> str:
    """Returns the embed description for the pr_ascension event"""
    user_name_end = message_content.find("** has unlocked")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** just ascended.\n\n'
        f'Yep. Just like that.\n\n'
        f'Congratulations!\n\n'
        f'Really hope you like dynamite tho, because you gotta see a lot of that.'
    )

    return description


async def get_pr_timetravel_description(message_content: str) -> str:
    """Returns the embed description for the pr_timetravel event"""
    user_name_end = message_content.find("** has traveled")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** just traveled in time!\n\n'
        f'To, uh, area 1.\n'
        f'Why would anyone do that?\n'
        f'Doesn\'t even have any gear anymore, lol, what a noob.'
    )

    return description


async def get_enchant_enchant_description(message_content: str) -> str:
    """Returns the embed description for the enchant_enchant event"""
    user_name_end = message_content.find("'s enchant")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    enchant_start_string = '~-~> '
    enchant_start = message_content.find(enchant_start_string) + len(enchant_start_string)
    enchant_end = message_content.find(' <~-~', enchant_start)
    enchant = message_content[enchant_start:enchant_end]

    description = (
        f'**{user_name}** used `enchant` like the cool kids do.\n\n'
        f'And managed to get a {enchant} enchant which only the super cool kids do.\n\n'
        f'See, transcenders, _that\'s_ how you do it.\n\n'
        f'Now someone get them some ice packs for their wrists.'
    )

    return description


async def get_enchant_refine_description(message_content: str) -> str:
    """Returns the embed description for the enchant_refine event"""
    user_name_end = message_content.find("'s refine")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    enchant_start_string = '~-~> '
    enchant_start = message_content.find(enchant_start_string) + len(enchant_start_string)
    enchant_end = message_content.find(' <~-~', enchant_start)
    enchant = message_content[enchant_start:enchant_end]

    description = (
        f'**{user_name}** refined their gear and got a {enchant} enchant as a reward.\n\n'
        f'Which is cool and all, but can you do that with `enchant`?'
    )

    return description


async def get_enchant_transmute_description(message_content: str) -> str:
    """Returns the embed description for the enchant_transmute event"""
    user_name_end = message_content.find("'s transmute")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    enchant_start_string = '~-~> '
    enchant_start = message_content.find(enchant_start_string) + len(enchant_start_string)
    enchant_end = message_content.find(' <~-~', enchant_start)
    enchant = message_content[enchant_start:enchant_end]

    description = (
        f'**{user_name}** transmuted something and somehow got a {enchant} enchant.\n\n'
        f'Listen to all the cheers!\n\n'
        f'Just kidding, we are just laughing because you can\'t use `transcend` yet.'
    )

    return description


async def get_enchant_transcend_description(message_content: str) -> str:
    """Returns the embed description for the enchant_godly event"""
    user_name_end = message_content.find("'s transcend")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    enchant_start_string = '~-~> '
    enchant_start = message_content.find(enchant_start_string) + len(enchant_start_string)
    enchant_end = message_content.find(' <~-~', enchant_start)
    enchant = message_content[enchant_start:enchant_end]

    description = (
        f'**{user_name}** transcended reality and got a {enchant} enchant.\n\n'
        f'Stop spending so much money on enchants!\n\n'
        f'Seriously, `enchant` is way cheaper.'
    )

    return description


async def get_gambling_coinflip_description(message_content: str) -> str:
    """Returns the embed description for the gambling_coinflip event"""
    user_name_end = message_content.find("'s coinflip")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    winnings_start_string = 'YOU WON '
    winnings_start = message_content.find(winnings_start_string) + len(winnings_start_string)
    winnings_end = message_content.find(' COINS', winnings_start)
    winnings = message_content[winnings_start:winnings_end]
    try:
        winnings = int(winnings.replace(',','').strip())
    except Exception as error:
        await database.log_error(
            f'Error: {error}\nFunction: get_gambling_coinflip_description\nwinnings: {winnings}'
        )
        return

    description = (
        f'But if you do, at least do it in style!\n\n'
        f'Like **{user_name}** who just threw a coin that landed on its side, winning them **{winnings:,}** coins.'
    )

    if winnings < 1_000_000:
        description = (
            f'{description}\n\n'
            f'Now imagine what they would have gotten if they hadn\'t chickened out by betting such a small '
            f'amount, lol.'
        )

    return description


async def get_gambling_slots_description(message_content: str) -> str:
    """Returns the embed description for the gambling_slots event"""
    user_name_end = message_content.find("'s slots")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    winnings_start_string = 'You won **'
    winnings_start = message_content.find(winnings_start_string) + len(winnings_start_string)
    winnings_end = message_content.find('** coins', winnings_start)
    winnings = message_content[winnings_start:winnings_end]
    try:
        winnings = int(winnings.replace(',','').strip())
    except Exception as error:
        await database.log_error(
            f'Error: {error}\nFunction: get_gambling_slots_description\nwinnings: {winnings}'
        )
        return

    description = (
        f'**{user_name}** somehow got the same icon 5 times at the slot machine and won **{winnings:,}** coins.\n\n'
        f'Hope they get out of there quickly tho, pretty sure the casino owner is on to them.'
    )

    if winnings < 1_000_000:
        description = (
            f'{description}\n\n'
            f'Wait, never mind, she doesn\'t care, she\'s too busy laughing about that low bet.'
        )

    return description


async def get_horse_tier_description(message_content: str) -> str:
    """Returns the embed description for the gambling_slots event"""

    horse_tier_emojis = {
        'I': emojis.HORSE_T1,
        'II': emojis.HORSE_T2,
        'III': emojis.HORSE_T3,
        'IV': emojis.HORSE_T4,
        'V': emojis.HORSE_T5,
        'VI': emojis.HORSE_T6,
        'VII': emojis.HORSE_T7,
        'VIII': emojis.HORSE_T8,
        'IX': emojis.HORSE_T9,
        'X': emojis.HORSE_T10
    }

    first_failed_attemps_location = message_content.find("accumulated failed attempts")
    user_name_1_end = message_content.find("'s accumulated failed attempts: 0")
    user_name_1_start = message_content.rfind("'", 0, user_name_1_end) + 1
    if (user_name_1_start < first_failed_attemps_location) and (user_name_1_end > first_failed_attemps_location):
        user_name_1_start = message_content.rfind("\\n", 0, user_name_1_end) + 2
    user_name_1 = message_content[user_name_1_start:user_name_1_end]
    user_tier_search = f'{user_name_1}** got a tier '
    user_tier_start = message_content.find(user_tier_search) + len(user_tier_search)
    user_tier_end = message_content.find(' <:tier', user_tier_start)
    user_tier = message_content[user_tier_start:user_tier_end]

    user_name_2 = None
    if message_content.count('failed attempts: 0') == 2:
        user_name_2_search = "'s accumulated failed attempts: 0"
        user_name_2_end = message_content.find(user_name_2_search, user_name_1_end + len(user_name_2_search))
        user_name_2_start = message_content.rfind("\\n", 0, user_name_2_end) + 2
        user_name_2 = message_content[user_name_2_start:user_name_2_end]

    if user_name_2 is None:
        description = (
            f'**{user_name_1}**\'s horse just tiered up while having completely inappropriate fun with another '
            f'horse! Neigh!\n\n'
            f'Congratulations, it\'s a little tier {user_tier} {horse_tier_emojis[user_tier]}!'
        )
    else:
        description = (
            f'The horses of **{user_name_1}** and **{user_name_2}** had some secret fun and liked it so much, '
            f'they BOTH tiered up! Wot!\n\n'
            f'They are now both tier {user_tier} {horse_tier_emojis[user_tier]}!'
        )

    return description


async def get_event_boss_description(message_content: str) -> str:
    """Returns the embed description for the event_boss event"""
    user_names_search = 'Players: '
    user_names_start = message_content.find(user_names_search) + len(user_names_search)
    user_names_end = message_content.find("',", user_names_start)
    user_names = message_content[user_names_start:user_names_end]

    user_name_list = []
    user_name_start = 0
    for player in range(0, user_names.count(', ') + 1):
        user_name_end = user_names.find(', ', user_name_start)
        if user_name_end == -1:
            user_name = user_names[user_name_start:]
        else:
            user_name = user_names[user_name_start:user_name_end]
        user_name_list.append(user_name)
        user_name_start = user_name_end + 2

    description_user_names = ''
    for index, user_name in enumerate(user_name_list):
        if index == len(user_name_list) - 1:
            description_user_names = f'{description_user_names} and **{user_name}**'
        else:
            description_user_names = f'{description_user_names}, **{user_name}**'
    description_user_names = description_user_names.lstrip(', ')

    description = (
        f'{description_user_names} defeated a {emojis.EVENT_BOSS} legendary boss in an epic fight! Wooh!\n\n'
        f'Why didn\'t YOU help, though.'
    )

    return description


async def get_event_lb_description(message_content: str) -> str:
    """Returns the embed description for the event_lb event"""
    user_name_end = message_content.find("** uses a")
    user_name_start = message_content.rfind(' **', 0, user_name_end) + 3
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** used a magic spell on a lootbox for some reason which then evolved into an '
        f'{emojis.emojis.LB_OMEGA} OMEGA lootbox.\n\n'
        f'Everything about this sounds unauthorized, so I\'ll be reporting this to the Ministry of Magic.'
    )

    return description


async def get_event_enchant_description(message_content: str) -> str:
    """Returns the embed description for the event_enchant event"""
    user_name_end = message_content.find("** tries to enchant")
    user_name_start = message_content.rfind(' **', 0, user_name_end) + 3
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** was too dumb to enchant stuff properly, so they enchanted the same thing twice.\n\n'
        f'Somehow that actually worked and got them an ULTRA-EDGY enchantment.\n\n'
        f'{emojis.SUS}'
    )

    return description


async def get_event_farm_description(message_content: str) -> str:
    """Returns the embed description for the event_farm event"""
    user_name_end = message_content.find("** HITS THE FLOOR")
    user_name_start = message_content.rfind(' **', 0, user_name_end) + 3
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** fought a seed (why would you do that) by hitting the floor with their fists (what) '
        f'and leveled up 20 times (??).\n\n'
        f'Everything about this seems weird, so I\'m pretty sure they hacked themselves 20 levels '
        f'and invented a lame excuse to cover it up.'
    )

    return description


async def get_event_heal_description(message_content: str) -> str:
    """Returns the embed description for the event_heal event"""
    user_name_end = message_content.find("** killed the")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** encountered a poor mysterious and helpless man.\n\n'
        f'Instead of leaving him be like a sensible person would, '
        f'they decided to kill him.\n\n'
        f'Enjoy your level up, I guess. Hope you feel bad.'
    )

    return description


async def get_event_jail_description(message_content: str) -> str:
    """Returns the embed description for the event_jail event"""
    user_name_end = message_content.find("** killed the")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** killed the EPIC guard!\n\n'
        f'Now there is another EPIC guard.\n\n'
        f'Uh. So. Yay?'
    )

    return description