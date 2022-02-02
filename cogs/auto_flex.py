# events.py
"""Contains the on_message handling for auto flex alerts"""

import re

import discord
from discord.ext import commands

import database
from resources import exceptions, emojis, logs, settings


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

            # Update current user TT
            if message.embeds:
                embed = message.embeds[0]
                search_strings = ['\'s profile', '\'s progress', '\'s time travel']
                if any(string in message_author.lower() for string in search_strings) and embed.fields:
                    icon_url = embed.author.icon_url
                    user_id = user_name = user = None
                    try:
                        user_id = int(re.search("avatars\/(.+?)\/", icon_url).group(1))
                    except:
                        try:
                            user_name = re.search("^(.+?)'s", embed.author.name).group(1)
                            user_name = user_name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                        except Exception as error:
                            await message.add_reaction(emojis.WARNING)
                            await database.log_error(error)
                            return
                    if user_id is not None:
                        user = await message.guild.fetch_member(user_id)
                    else:
                        for member in message.guild.members:
                            member_name = member.name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                            if member_name == user_name:
                                user = member
                                break
                    if user is None:
                        await message.add_reaction(emojis.WARNING)
                        await database.log_error(f'User not found in profile message: {message}')
                        return
                    if 'time travel' in message_author.lower():
                        progress_field = embed.description
                        if 'you will come back to the beginning' in progress_field.lower(): return
                        try:
                            current_tt = re.search('Time travels\*\*: (.+?)\\n', progress_field).group(1)
                            current_tt = int(current_tt)
                        except:
                            current_tt = 0
                    else:
                        progress_field = embed.fields[0].value
                        try:
                            current_tt = re.search('Time travels\*\*: (.+?)$', progress_field).group(1)
                            current_tt = int(current_tt)
                        except:
                            current_tt = 0
                    try:
                        user_settings: database.User = await database.get_user(user.id)
                        await user_settings.update(current_tt=current_tt)
                    except exceptions.NoDataFoundError:
                        user_settings = await database.insert_user(user.id, current_tt)

            event = ''
            if 'is this a **dream**????' in message_content.lower():
                event = 'work_ultra'
                logs.logger.info(message_content)
            if 'wwwwwoooooooooaaaaaaaa!!!!1' in message_content.lower():
                event = 'work_hyper'
                logs.logger.info(message_content)
            if 'pet adventure rewards' in message_content.lower() and 'ultra log' in message_content.lower():
                event = 'pet_ultra'
                logs.logger.info(message_content)
            if ('this pet has obtained the **ascended** skill' in message_content.lower()
                or 'this pet has advanced its **ascended** skill' in message_content.lower()):
                event = 'pet_ascend'
                logs.logger.info(message_content)
            if ('you have got a new pet!' in message_content.lower()
                and '<:epicskill' in message_content.lower()
                and '[f]' in message_content.lower()):
                event = 'pet_epic'
                logs.logger.info(message_content)
            if 'the melting heat required to forge this sword was so much' in message_content.lower():
                event = 'forge_godly'
                logs.logger.info(message_content)
            if 'lootbox opened! (x100)' in message_content.lower():
                event = 'lb_100'
                logs.logger.info(message_content)
            if 'found and killed' in message_content.lower() and 'omega lootbox' in message_content.lower():
                event = 'lb_omega'
                logs.logger.info(message_content)
            if 'are hunting together' in message_content.lower() and 'omega lootbox' in message_content.lower():
                user_name_search = "** and **"
                user_name_end = message_content.find(user_name_search)
                user_name_start = message_content.rfind('**', 0, user_name_end) + 2
                user_name = message_content[user_name_start:user_name_end]
                lb_amount_end = message_content.rfind(' <:OMEGA')
                lb_amount_start_search = f'**{user_name}** got '
                lb_amount_start = message_content.rfind(lb_amount_start_search, 0, lb_amount_end) + len(lb_amount_start_search)
                if lb_amount_end - lb_amount_start > 3:
                    event = 'lb_omega_partner'
                    logs.logger.info(message_content)
                else:
                    event = 'lb_omega'
                    logs.logger.info(message_content)
            # Christmas godly present
            if (('found and killed' in message_content.lower() or 'are hunting together' in message_content.lower())
                and 'godly present' in message_content.lower()):
                event = 'present_godly'
                logs.logger.info(message_content)
            if 'seed in the ground' in message_content.lower() and 'godly present' in message_content.lower():
                event = 'present_godly_farm'
                logs.logger.info(message_content)
            if 'well done,' in message_content.lower() and 'godly present' in message_content.lower():
                event = 'present_godly_training'
                logs.logger.info(message_content)
            if ((('quest' in message_content.lower() and 'completed!' in message_content.lower()) or 'wave #1' in message_content.lower())
                and 'godly present' in message_content.lower()):
                event = 'present_godly_quest'
                logs.logger.info(message_content)
            if (('found and killed' in message_content.lower() or 'are hunting together' in message_content.lower())
                  and 'godly lootbox' in message_content.lower()):
                event = 'lb_godly'
                logs.logger.info(message_content)
            if (('found and killed' in message_content.lower() or 'are hunting together' in message_content.lower())
                  and 'mysterious lootbox' in message_content.lower()):
                event = 'lb_mysterious'
                logs.logger.info(message_content)
            if 'edgy lootbox opened!' in message_content.lower() and 'ultra log' in message_content.lower():
                event = 'lb_edgy_ultra'
                logs.logger.info(message_content)
            if 'omega lootbox opened!' in message_content.lower() and 'ultra log' in message_content.lower():
                event = 'lb_omega_ultra'
                logs.logger.info(message_content)
            if 'godly lootbox opened!' in message_content.lower() and 'time travel' in message_content.lower():
                event = 'lb_godly_tt'
                logs.logger.info(message_content)
            if 'has unlocked the **ascended skill**' in message_content.lower():
                event = 'pr_ascension'
                logs.logger.info(message_content)
            if 'has traveled in time' in message_content.lower():
                event = 'pr_timetravel'
                logs.logger.info(message_content)
            if "wait what? it landed on its side" in message_content.lower():
                winnings_start_string = 'YOU WON '
                winnings_start = message_content.find(winnings_start_string) + len(winnings_start_string)
                winnings_end = message_content.find(' COINS', winnings_start)
                winnings = message_content[winnings_start:winnings_end]
                try:
                    winnings = int(winnings.replace(',','').strip())
                except Exception as error:
                    await database.log_error(
                        f'Error: {error}\nFunction: on_message (coinflip)\nwinnings: {winnings}'
                    )
                    return
                if winnings < 100_000_000:
                    return
                event = 'gambling_coinflip'
                logs.logger.info(message_content)
            if "'s slots" in message_content.lower():
                icons = ['💎','💯','🎁','✨','🍀']
                if any(message_content.lower().count(icon) == 5 for icon in icons):
                    winnings_start_string = 'You won **'
                    winnings_start = message_content.find(winnings_start_string) + len(winnings_start_string)
                    winnings_end = message_content.find('** coins', winnings_start)
                    winnings = message_content[winnings_start:winnings_end]
                    try:
                        winnings = int(winnings.replace(',','').strip())
                    except Exception as error:
                        await database.log_error(
                            f'Error: {error}\nFunction: on_message (slots)\nwinnings: {winnings}'
                        )
                        return
                    if winnings < 100_000_000:
                        return
                    event = 'gambling_slots'
                    logs.logger.info(message_content)
            if ("'s wheel" in message_content.lower()) and ('you won' in message_content.lower()):
                message_content_check = (message_content
                                         .encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                                         .replace('U0001f7e6','').replace('U0001f7eb','').replace('U0001f7e7','')
                                         .replace('U0001f7e5','').replace('U0001f7e8','').replace('U0001f7e9',''))
                logs.logger.info(f'MESSAGE CONTENT CHECK\n{message_content_check}')
                board_check = (
                    ':black_large_square::black_large_square::black_large_square::small_red_triangle_down:'
                    ':black_large_square::black_large_square::black_large_square:n:black_large_square:'
                    ':black_large_square:U0001f7ea:black_large_square::black_large_square:'
                ).encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                if board_check in message_content_check:
                    winnings_start_string = 'You won **'
                    winnings_start = message_content.find(winnings_start_string) + len(winnings_start_string)
                    winnings_end = message_content.find('** coins', winnings_start)
                    winnings = message_content[winnings_start:winnings_end]
                    try:
                        winnings = int(winnings.replace(',','').strip())
                    except Exception as error:
                        await database.log_error(
                            f'Error: {error}\nFunction: on_message (wheel)\nwinnings: {winnings}'
                        )
                        return
                    if winnings < 1_000_000_000:
                        return
                    event = 'gambling_wheel'
                    logs.logger.info(message_content)
            if 'accumulated failed attempts: 0' in message_content.lower():
                event = 'horse_tier'
                logs.logger.info(message_content)
            if 'the legendary boss died! everyone leveled up' in message_content.lower():
                event = 'event_boss'
                logs.logger.info(message_content)
            if 'your lootbox has evolved to an omega lootbox' in message_content.lower():
                event = 'event_lb'
                logs.logger.info(message_content)
            if ('your sword got an ultra-edgy enchantment' in message_content.lower()
                  or 'your armor got an ultra-edgy enchantment' in message_content.lower()):
                event = 'event_enchant'
                logs.logger.info(message_content)
            if 'the seed surrendered' in message_content.lower():
                event = 'event_farm'
                logs.logger.info(message_content)
            if 'killed the mysterious man' in message_content.lower():
                event = 'event_heal'
                logs.logger.info(message_content)
            if 'killed the **epic guard**' in message_content.lower():
                event = 'event_jail'
                logs.logger.info(message_content)
            if ('fights the horde...' in message_content.lower()) and ('success!!' in message_content.lower()):
                event = 'event_hunt'
                logs.logger.info(message_content)
            if " ate " in message_content.lower() and "arena cookie"in message_content.lower():
                cookies_end = message_content.find(' <:arena')
                cookies_start = message_content.rfind('**', 0, cookies_end) + 2
                cookies = message_content[cookies_start:cookies_end]
                try:
                    cookies = int(cookies.replace(',','').strip())
                except Exception as error:
                    await database.log_error(
                        f'Error: {error}\nFunction: on_message (cookies)\nCookie amount: {cookies}'
                    )
                    return
                if cookies < 10_000:
                    return
                event = 'cookies'
                logs.logger.info(message_content)

            if event != '':
                guild_settings: database.Guild = await database.get_guild(message.guild)
                if guild_settings.auto_flex_enabled and guild_settings.auto_flex_channel_id != 0:
                    await self.bot.wait_until_ready()
                    auto_flex_channel = self.bot.get_channel(guild_settings.auto_flex_channel_id)
                    embed = await embed_auto_flex(message, message_content, event)
                    await auto_flex_channel.send(embed=embed)
                    await message.add_reaction(emojis.TATL)


# Initialization
def setup(bot):
    bot.add_cog(AutoFlexCog(bot))


# Embeds
async def embed_auto_flex(message: discord.Message, message_content:str, event: str) -> discord.Embed:
    """Auto flex embed"""

    flex_titles = {
        'work_ultra': f'{emojis.LOG_ULTRA} It\'s not a dream!',
        'work_hyper': f'{emojis.LOG_HYPER} Hyperino',
        'pet_ultra': f'{emojis.LOG_ULTRA} ULTRA l...azy',
        'pet_ascend': f'{emojis.SKILL_ASCENDED} No skill champ',
        'pet_epic': f'{emojis.SKILL_EPIC} EEEEEEEPIC',
        'forge_godly': f'{emojis.SWORD_GODLY} Almost a cookie',
        'lb_100': f'{emojis.SLOTS_100} Look at that pile!',
        'lb_omega': f'{emojis.LB_OMEGA} Ohh... shiny!',
        'lb_omega_partner': f'{emojis.LB_OMEGA} Oops, wrong recipient, lol',
        'lb_godly': f'{emojis.LB_GODLY} WAIT WHAT?',
        'lb_edgy_ultra': f'{emojis.LOG_ULTRA} It\'s just an EDGY, lol',
        'lb_omega_ultra': f'{emojis.LOG_ULTRA} That\'s a lot of wood',
        'lb_godly_tt': f'{emojis.TIME_TRAVEL} WHAT. THE. SHIT.',
        'pr_ascension': f'{emojis.ASCENSION} Up up and away',
        'pr_timetravel': f'{emojis.TIME_TRAVEL} Allons-y!',
        'gambling_coinflip': f'{emojis.COIN} Stop gambling, kids!',
        'gambling_slots': f'{emojis.SLOTS} JACKPOT',
        'gambling_wheel': f'{emojis.WHEEE} WHEEEEEEEEEEEEEEE.....',
        'horse_tier': f'{emojis.HORSE_T1} Horseback Mountain',
        'event_boss': f'{emojis.EVENT_BOSS} LEGEN... WAIT FOR IT... (seriously, wait for it, gonna be a while)',
        'event_lb': f'{emojis.LB_OMEGA} They did what now?',
        'event_enchant': f'{emojis.BOOM} Twice the fun',
        'event_farm': f'{emojis.CROSSED_SWORDS} Totally believable level up story',
        'event_heal': f'{emojis.LIFE_POTION} Very mysterious',
        'event_jail': f'{emojis.EPIC_GUARD} But... why?',
        'event_hunt': f'{emojis.ZOMBIE_EYE} Not quite a level',
        'cookies': f'{emojis.ARENA_COOKIE} This is the dumbest thing, lol',
        'lb_mysterious': f'{emojis.LB_MYSTERIOUS} What on earth is this?',
        'present_godly': f'{emojis.PRESENT_GODLY} Oh, hello Santa!',
        'present_godly_farm': f'{emojis.PRESENT_GODLY} Oh, hello Santa!',
        'present_godly_training': f'{emojis.PRESENT_GODLY} Oh, hello Santa!',
        'present_godly_quest': f'{emojis.PRESENT_GODLY} Oh, hello Santa!',
    }

    flex_description_functions = {
        'work_ultra': get_work_ultra_description,
        'work_hyper': get_work_hyper_description,
        'pet_ultra': get_pet_ultra_description,
        'pet_ascend': get_pet_ascend_description,
        'pet_epic': get_pet_epic_description,
        'forge_godly': get_forge_godly_description,
        'lb_100': get_lb_100_description,
        'lb_omega': get_lb_omega_description,
        'lb_omega_partner': get_lb_omega_partner_description,
        'lb_godly': get_lb_godly_description,
        'lb_edgy_ultra': get_lb_edgy_ultra_description,
        'lb_omega_ultra': get_lb_omega_ultra_description,
        'lb_godly_tt': get_lb_godly_tt_description,
        'pr_ascension': get_pr_ascension_description,
        'pr_timetravel': get_pr_timetravel_description,
        'gambling_coinflip': get_gambling_coinflip_description,
        'gambling_slots': get_gambling_slots_description,
        'gambling_wheel': get_gambling_wheel_description,
        'horse_tier': get_horse_tier_description,
        'event_boss': get_event_boss_description,
        'event_lb': get_event_lb_description,
        'event_enchant': get_event_enchant_description,
        'event_farm': get_event_farm_description,
        'event_heal': get_event_heal_description,
        'event_jail': get_event_jail_description,
        'event_hunt': get_event_hunt_description,
        'cookies': get_cookies_description,
        'lb_mysterious': get_lb_mysterious_description,
        'present_godly': get_present_godly_description,
        'present_godly_farm': get_present_godly_farm_description,
        'present_godly_training': get_present_godly_training_description,
        'present_godly_quest': get_present_godly_quest_description,
    }

    flex_thumbnails = {
        'work_ultra': 'https://c.tenor.com/4ReodhBihBQAAAAC/ruthe-biber.gif',
        'work_hyper': 'https://c.tenor.com/p8NKGRDxNvMAAAAC/rut-daniels-timber.gif',
        'pet_ultra': 'https://c.tenor.com/nwbxEGQINOsAAAAC/pet-dog.gif',
        'pet_ascend': 'https://c.tenor.com/yyiGOtquk74AAAAC/rocket-clicks-rocket.gif',
        'pet_epic': 'https://c.tenor.com/yEIrzx7iFU4AAAAC/dog-meme.gif',
        'forge_godly': 'https://c.tenor.com/OSYJN4DF0tEAAAAC/light-up.gif',
        'lb_100': 'https://c.tenor.com/gHygBs_JkKwAAAAi/moving-boxes.gif',
        'lb_omega': 'https://c.tenor.com/8yMrP1Cs7ykAAAAC/ninjala-ninjala-season6trailer.gif',
        'lb_omega_partner': 'https://c.tenor.com/l0wNXZN58S8AAAAC/delivery-kick.gif',
        'lb_godly': 'https://c.tenor.com/zBe7Ew1lzPYAAAAi/tkthao219-bubududu.gif',
        'lb_edgy_ultra': 'https://c.tenor.com/clnoM8TeSxcAAAAC/wait-what-unbelievable.gif',
        'lb_omega_ultra': 'https://c.tenor.com/dBaynU7zBaIAAAAi/love-box.gif',
        'lb_godly_tt': 'https://c.tenor.com/-BVQhBulOmAAAAAC/bruce-almighty-morgan-freeman.gif',
        'pr_ascension': 'https://c.tenor.com/Jpx1xCUOyz8AAAAC/ascend.gif',
        'pr_timetravel': 'https://c.tenor.com/VKwvOapbLeMAAAAC/boris-soiree-disco.gif',
        'gambling_coinflip': 'https://c.tenor.com/GtTxw8NRrlwAAAAC/dbh-connor.gif',
        'gambling_slots': 'https://c.tenor.com/vh6UO80RFmYAAAAC/toilet-paper-slot-machine.gif',
        'gambling_wheel': 'https://c.tenor.com/lmetHrqB8k4AAAAC/flossen-bubbles.gif',
        'horse_tier': 'https://c.tenor.com/FMdPKbgHXbsAAAAC/horse-laugh.gif',
        'event_boss': 'https://c.tenor.com/dAMi0gNJQeIAAAAC/peach-cat.gif',
        'event_lb': 'https://c.tenor.com/6WfJrQYFXlYAAAAC/magic-kazaam.gif',
        'event_enchant': 'https://c.tenor.com/gAuPzxRCVw8AAAAC/link-dancing.gif',
        'event_farm': 'https://c.tenor.com/OEIwT0KEyREAAAAC/homer-fist.gif',
        'event_heal': 'https://c.tenor.com/IfAs08au8IYAAAAd/he-died-in-mysterious-circumstances-the-history-guy.gif',
        'event_jail': 'https://c.tenor.com/txj6Fp2ipqMAAAAC/prison-jail.gif',
        'event_hunt': 'https://c.tenor.com/PQ5Q7_GwZucAAAAi/panda-zombie-smiling.gif',
        'cookies': 'https://c.tenor.com/mbs-siKKowoAAAAd/cookie-monster-cookie-for-you.gif',
        'lb_mysterious': 'https://c.tenor.com/3ViKggOJ8PAAAAAC/spongebob-empty-box.gif',
        'present_godly': 'https://c.tenor.com/V0Z6XInA21UAAAAC/teletubbies-dipsy.gif',
        'present_godly_farm': 'https://c.tenor.com/V0Z6XInA21UAAAAC/teletubbies-dipsy.gif',
        'present_godly_training': 'https://c.tenor.com/V0Z6XInA21UAAAAC/teletubbies-dipsy.gif',
        'present_godly_quest': 'https://c.tenor.com/V0Z6XInA21UAAAAC/teletubbies-dipsy.gif',
    }

    embed_title = flex_titles[event]
    embed_description = await flex_description_functions[event](message_content, message)

    if '**FlyingPanda**' in embed_description:
        #embed_description = f'{embed_description}\n\n:panda_face:'
        pass

    if '**nad**' in embed_description:
        #embed_description = f'{embed_description}\n\nThis is not Neat {emojis.SLAP}'
        pass

    if '**RaYawsT**' in embed_description:
        #embed_description = f'{embed_description}\n\nRay-Ban® {emojis.CAT_GUN}'
        pass

    embed = discord.Embed(
        color = settings.EMBED_COLOR,
        title = embed_title,
        description = f'{embed_description}\n\n[Check it out]({message.jump_url})'
    )

    embed.set_thumbnail(url=flex_thumbnails[event])

    return embed


# Functions
async def get_work_ultra_description(message_content: str, message: discord.Message) -> str:
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
        f'**{user_name}** just cut down {log_amount} {emojis.LOG_ULTRA} ULTRA logs with a chainsaw. In their mouth.\n\n'
        f'Look. Let\'s all just... back away... slowly...'
    )

    return description


async def get_work_hyper_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the work_hyper event"""
    user_name_end = message_content.find('** is chopping')
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    log_amount_string = '** got '
    log_amount_start = message_content.find(log_amount_string) + len(log_amount_string)
    log_amount_end = message_content.find(' <', log_amount_start)
    log_amount = message_content[log_amount_start:log_amount_end].strip()

    description = (
        f'**{user_name}** was taking a walk in the park, when suddenly a tree fell over and split into {log_amount} {emojis.LOG_HYPER} HYPER logs.\n\n'
        f'You couldn\'t make this up, honestly.\n\n'
        f'Oh wait. You can.'
    )

    return description


async def get_pet_ultra_description(message_content: str, message: discord.Message) -> str:
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
        f'**{user_name}** got {log_amount_total} {emojis.LOG_ULTRA} ULTRA logs from their pets.\n\n'
        f'Why? Nobody knows. But I call this illegal pet labor, so I will report it.'
    )

    return description


async def get_pet_ascend_description(message_content: str, message: discord.Message) -> str:
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


async def get_forge_godly_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the forge_godly event"""
    user_name_string = 'exhausted'
    user_name_start = message_content.find(user_name_string) + len(user_name_string) + 1
    user_name_end = message_content.find(' earned', user_name_start)
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**Someone** (idk, go check for yourself) forged a GODLY sword!\n\n'
        f'Wowzers, what an amazing thing!\n\n'
        f'Oh wait. It has 0 AT, lol.\n\n'
        f'Some folks really to anything for fame, I swear.'
    )

    return description


async def get_lb_100_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the forge_godly event"""
    lootbox_type_emoji = {
        'common': emojis.LB_COMMON,
        'uncommon': emojis.LB_UNCOMMON,
        'rare': emojis.LB_RARE,
        'epic': emojis.LB_EPIC,
        'edgy': emojis.LB_EDGY,
        'omega': emojis.LB_OMEGA,
        'godly': emojis.LB_GODLY
    }

    user_name_end = message_content.find("'s lootbox")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    lb_type_end = message_content.find(' lootbox opened!')
    lb_type_start = message_content.rfind(' ', 0, lb_type_end) + 1
    lb_type = message_content[lb_type_start:lb_type_end]

    try:
        lb_emoji = lootbox_type_emoji[lb_type.lower()]
    except Exception as error:
        await database.log_error(f'Error: {error}\nFunction: get_lb_100_description\nlootbox_type: {lb_type}')
        return

    description = (
        f'**{user_name}** opened 100 {lb_emoji} {lb_type} lootboxes at once.\n\n'
        f'You know what that means? They opened **100** lootboxes and not a single one of those triggered the lootbox '
        f'event.\n'
        f'Woahaha.'
    )

    return description


async def get_lb_omega_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_omega event"""
    hunt_together = True if 'are hunting together' in message_content else False
    if hunt_together:
        user_name_search = "** and **"
        user_name_end = message_content.find(user_name_search)
        partner_name_start = user_name_end + len(user_name_search)
        partner_name_end = message_content.find("** are", partner_name_start)
        partner_name = message_content[partner_name_start:partner_name_end]
    else:
        user_name_end = message_content.find("** found and killed")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    lb_amount_end = message_content.find(' <:OMEGA')
    lb_amount_start_search = f'**{user_name}** got '
    lb_amount_start = message_content.rfind(lb_amount_start_search, 0, lb_amount_end) + len(lb_amount_start_search)
    lb_amount = message_content[lb_amount_start:lb_amount_end]

    try:
        lb_amount = int(lb_amount.strip())
    except Exception as error:
        await database.log_error(f'Error: {error}\nFunction: get_lb_omega_description\nlootbox_amount: {lb_amount}')
        return

    if '(but stronger)' not in message_content:
        description = (
            f'**{user_name}** just found {lb_amount} {emojis.LB_OMEGA} OMEGA lootbox completely without any hardmodes!\n\n'
            f'Take this, ascended hardmoding cheap mode people! That\'s how you do it.'
        )
    else:
        description = (
            f'**{user_name}** just found {lb_amount} {emojis.LB_OMEGA} OMEGA lootbox! Oh joy, such a rare thing!\n'
            f'Huh.\n'
            f'I mean.\n'
            f'Yes.'
        )

    return description


async def get_lb_omega_partner_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_omega_partner event"""

    user_name_search = "** and **"
    user_name_end = message_content.find(user_name_search)
    partner_name_start = user_name_end + len(user_name_search)
    partner_name_end = message_content.find("** are", partner_name_start)
    partner_name = message_content[partner_name_start:partner_name_end]
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    lb_amount_end = message_content.rfind(' <:OMEGA')
    lb_amount_start_search = f'**{partner_name}** got '
    lb_amount_start = message_content.rfind(lb_amount_start_search, 0, lb_amount_end) + len(lb_amount_start_search)
    lb_amount = message_content[lb_amount_start:lb_amount_end]

    try:
        lb_amount = int(lb_amount.strip())
    except Exception as error:
        await database.log_error(f'Error: {error}\nFunction: get_lb_omega_partner_description\nlootbox_amount: {lb_amount}')
        return

    description = (
        f'So, funny story.\n'
        f'**{user_name}** ordered an {lb_amount} {emojis.LB_OMEGA} OMEGA lootbox and it just got delivered.\n\n'
        f'...to **{partner_name}**\'s address.\n'
        f'LMAO.'
    )

    return description


async def get_lb_godly_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_godly event"""
    hunt_together = True if 'are hunting together' in message_content else False

    if hunt_together:
        user_name_search = "** and **"
        user_name_end = message_content.find(user_name_search)
        partner_name_start = user_name_end + len(user_name_search)
        partner_name_end = message_content.find("** are", partner_name_start)
        partner_name = message_content[partner_name_start:partner_name_end]
    else:
        user_name_end = message_content.find("** found and killed")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    lb_amount_end = message_content.find(' <:GODLY')
    lb_amount_start_search = f'**{user_name}** got '
    lb_amount_start = message_content.rfind(lb_amount_start_search, 0, lb_amount_end) + len(lb_amount_start_search)
    partner_loot = False
    if hunt_together and lb_amount_end - lb_amount_start > 3:
        lb_amount_start_search_partner = f'**{partner_name}** got '
        lb_amount_start = (message_content
                           .rfind(lb_amount_start_search_partner, 0, lb_amount_end)
                           + len(lb_amount_start_search_partner))
        partner_loot = True

    lb_amount = message_content[lb_amount_start:lb_amount_end]
    try:
        lb_amount = int(lb_amount.strip())
    except Exception as error:
        await database.log_error(f'Error: {error}\nFunction: get_lb_godly_description\nlootbox_amount: {lb_amount}')
        return

    description = (
        f'**{user_name}** just found {lb_amount} {emojis.LB_GODLY} GODLY lootbox??!\n\n'
        f'I\'m pretty sure this is illegal und should be reported.'
    )

    if partner_loot:
        description = f'{description}\n\n(Hope they didn\'t party too hard, the lootbox got stolen by their partner lol)'

    return description


async def get_lb_edgy_ultra_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_edgy_ultra event"""
    user_name_end = message_content.find("'s lootbox")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    lb_amount_end = message_content.find(' <:ULTRA')
    lb_amount_start = message_content.rfind('+', 0, lb_amount_end) + 1
    lb_amount = message_content[lb_amount_start:lb_amount_end]
    try:
        lb_amount = int(lb_amount.strip())
    except Exception as error:
        await database.log_error(
            f'Error: {error}\nFunction: get_lb_edgy_ultra_description\nlog_amount: {lb_amount}'
        )
        return

    description = (
        f'Look at **{user_name}**, opening that {emojis.LB_EDGY} EDGY lootbox like it\'s worth something, haha.\n\n'
        f'See. All he got is {lb_amount} lousy {emojis.LOG_ULTRA} ULTRA log.\n\n'
        f'...\n\n'
        f'**WAIT A SECOND.**'
    )

    return description


async def get_lb_omega_ultra_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_omega_ultra event"""
    user_name_end = message_content.find("'s lootbox")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    lb_amount_end = message_content.find(' <:ULTRA')
    lb_amount_start = message_content.rfind('+', 0, lb_amount_end) + 1
    lb_amount = message_content[lb_amount_start:lb_amount_end]
    try:
        lb_amount = int(lb_amount.strip())
    except Exception as error:
        await database.log_error(
            f'Error: {error}\nFunction: get_lb_omega_ultra_description\nlog_amount: {lb_amount}'
        )
        return

    description = (
        f'**{user_name}** opened an {emojis.LB_OMEGA} OMEGA lootbox!\n\n'
        f'How exciting. I think. Or not.\n\n'
        f'Wait! They found {lb_amount} {emojis.LOG_ULTRA} ULTRA log in there!\n\n'
        f'That\'s how you get caught hacking, kids, time to ban.\n'
        f'{emojis.POLICE}'
    )

    return description


async def get_lb_godly_tt_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_godly_tt event"""
    user_name_end = message_content.find("'s lootbox")
    user_name_start = message_content.rfind('"', 0, user_name_end) + 1
    user_name = message_content[user_name_start:user_name_end]

    tt_amount_end = message_content.find(' :cyclone')
    tt_amount_start = message_content.rfind('+', 0, tt_amount_end) + 1
    tt_amount = message_content[tt_amount_start:tt_amount_end]
    try:
        tt_amount = int(tt_amount.strip())
    except Exception as error:
        await database.log_error(
            f'Error: {error}\nFunction: get_lb_godly_tt_description\ntt_amount: {tt_amount}'
        )
        return

    description = (
        f'So.\n**{user_name}** opened an {emojis.LB_GODLY} GODLY lootbox.\nThat\'s cool.\n\n'
        f'BUT.\nFor some reason they found {tt_amount} {emojis.TIME_TRAVEL} fucking time travels in there. HOW?!\n\n'
        f'This is probably a world first, so expect to be blacklisted from the game.\n'
        f'Before that, go share it in the EROS loot channel tho, they will go crazy.'
    )

    return description


async def get_pr_ascension_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the pr_ascension event"""
    user_name_end = message_content.find("** has unlocked")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** just ascended.\n\n'
        f'Yep. Just like that. Congratulations!\n\n'
        f'Really hope you like dynamite tho, because you\'re gonna see a lot of that.'
    )

    return description


async def get_pr_timetravel_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the pr_timetravel event"""
    user_name_end = message_content.find("** has traveled")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]
    user_name = user_name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
    user = None
    for member in message.guild.members:
        member_name = member.name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
        if member_name == user_name:
            user = member
            break
    if user is None:
        await database.log_error(f'User not found in time travel message: {message}')
        raise ValueError
    try:
        user_settings: database.User = await database.get_user(user.id)
        description = (
            f'**{user.name}** just sold all of their earthly belongings (I swear, all they think about is cash these '
            f'days) and entered time travel **{user_settings.current_tt + 1}**!\n\n'
            f'Have fun with that basic sword.'
        )
        new_tt = user_settings.current_tt + 1
        await user_settings.update(current_tt=new_tt)
    except exceptions.NoDataFoundError:
        description = (
            f'**{user_name}** just sold all of their earthly belongings (I swear, all they think about is cash these '
            f'days) and entered a new time travel!\n\n'
            f'Have fun with that basic sword.'
        )

    return description


async def get_gambling_coinflip_description(message_content: str, message: discord.Message) -> str:
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


async def get_gambling_slots_description(message_content: str, message: discord.Message) -> str:
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


async def get_gambling_wheel_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the gambling_wheel event"""
    user_name_end = message_content.find("'s wheel")
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
            f'Error: {error}\nFunction: get_gambling_wheel_description\nwinnings: {winnings}'
        )
        return

    description = (
        f'**{user_name}** spun the wheel and... won the main prize! **{winnings:,}** coins to be exact!\n\n'
        f'Pretty sure they\'re going to lose it all tho since wheel is the worst gambling command of all.\n'
        f'(Don\'t tell them, where\'s the fun in that.)'
    )

    if winnings < 1_000_000:
        description = (
            f'{description}\n\n'
            f'Next time try to bet something higher btw, all that luck for those few coins, lol.'
        )

    return description


async def get_horse_tier_description(message_content: str, message: discord.Message) -> str:
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
    user_tier_search = f'{user_name_1} got a tier '
    user_tier_start = message_content.find(user_tier_search) + len(user_tier_search)
    user_tier_end = message_content.find(' <:tier', user_tier_start)
    user_tier = message_content[user_tier_start:user_tier_end]
    user_horse_name_search = "it's called "
    user_horse_name_start = message_content.find(user_horse_name_search, user_tier_end) + len(user_horse_name_search)
    user_horse_name_end = message_content.find(' !', user_horse_name_start)
    user_horse_name = message_content[user_horse_name_start:user_horse_name_end]

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
            f'Congratulations, it\'s a little tier {user_tier} {horse_tier_emojis[user_tier]}!\n\n'
            f'(Who names their horse **{user_horse_name}** tho, seriously.)'
        )
    else:
        description = (
            f'The horses of **{user_name_1}** and **{user_name_2}** had some secret fun and liked it so much, '
            f'they BOTH tiered up! Wot!\n\n'
            f'They are now both tier {user_tier} {horse_tier_emojis[user_tier]}!'
        )

    return description


async def get_event_boss_description(message_content: str, message: discord.Message) -> str:
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
        f'Somehow all of them survived, too, so we still have to keep up with them, I guess.'
    )

    return description


async def get_event_lb_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the event_lb event"""
    user_name_end = message_content.find("** uses a")
    user_name_start = message_content.rfind(' **', 0, user_name_end) + 3
    user_name = message_content[user_name_start:user_name_end]

    description = (
        f'**{user_name}** used a magic spell on a lootbox for some reason which then evolved into an '
        f'{emojis.LB_OMEGA} OMEGA lootbox.\n\n'
        f'Everything about this sounds unauthorized, so I\'ll be reporting this to the Ministry of Magic.'
    )

    return description


async def get_event_enchant_description(message_content: str, message: discord.Message) -> str:
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


async def get_event_farm_description(message_content: str, message: discord.Message) -> str:
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


async def get_event_heal_description(message_content: str, message: discord.Message) -> str:
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


async def get_event_jail_description(message_content: str, message: discord.Message) -> str:
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


async def get_event_hunt_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the event_hunt event"""
    user_name_end = message_content.find("** fights the horde")
    user_name_start = message_content.rfind(' **', 0, user_name_end) + 3
    user_name = message_content[user_name_start:user_name_end]

    zombie_amount_end = message_content.find(" zombies")
    zombie_amount_search = 'just '
    zombie_amount_start = message_content.rfind(zombie_amount_search, 0, zombie_amount_end) + len(zombie_amount_search)
    zombie_amount = message_content[zombie_amount_start:zombie_amount_end]

    try:
        zombie_amount = int(zombie_amount.strip())
    except Exception as error:
        await database.log_error(
            f'Error: {error}\nFunction: get_event_hunt_description\zombie_amount: {zombie_amount}'
        )
        return

    description = (
        f'**{user_name}** killed a whole horde of zombies!\n\n'
        f'Well, actually, it was just {zombie_amount} zombies, lol.\n'
        f'Does that even qualify as a flex {emojis.SUS}'
    )

    return description


async def get_cookies_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the cookies event"""
    user_name_end = message_content.find("** ate")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    cookies_end = message_content.find(' <:arena')
    cookies_start = message_content.rfind('**', 0, cookies_end) + 2
    cookies = message_content[cookies_start:cookies_end]
    try:
        cookies = int(cookies.replace(',','').strip())
    except Exception as error:
        await database.log_error(
            f'Error: {error}\nFunction: get_cookies_description\nCookie amount: {cookies}'
        )
        return

    description = (
        f'**{user_name}** ate {cookies:,} cookies.\n\n'
        f'**{cookies:,} COOKIES.**\n\n'
        f'**HAVE YOU **ANY** IDEA HOW MANY LEVELS THAT WOULD BE IF THEY COOKED SUPER COOKIES?**\n'
        'Achievement, they say. Bah. Nonsense I say.'
    )

    return description


async def get_lb_mysterious_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_mysterious event"""
    hunt_together = True if 'are hunting together' in message_content else False

    if hunt_together:
        user_name_search = "** and **"
        user_name_end = message_content.find(user_name_search)
        partner_name_start = user_name_end + len(user_name_search)
        partner_name_end = message_content.find("** are", partner_name_start)
        partner_name = message_content[partner_name_start:partner_name_end]
    else:
        user_name_end = message_content.find("** found and killed")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    lb_amount_end = message_content.find(' <:mysterious')
    lb_amount_start_search = f'**{user_name}** got '
    lb_amount_start = message_content.rfind(lb_amount_start_search, 0, lb_amount_end) + len(lb_amount_start_search)
    partner_loot = False
    if hunt_together and lb_amount_end - lb_amount_start > 3:
        lb_amount_start_search_partner = f'**{partner_name}** got '
        lb_amount_start = (message_content
                           .rfind(lb_amount_start_search_partner, 0, lb_amount_end)
                           + len(lb_amount_start_search_partner))
        partner_loot = True

    lb_amount = message_content[lb_amount_start:lb_amount_end]
    try:
        lb_amount = int(lb_amount.strip())
    except Exception as error:
        await database.log_error(f'Error: {error}\nFunction: get_lb_mysterious_description\nlootbox_amount: {lb_amount}')
        return

    description = (
        f'So, uh, **{user_name}** found {lb_amount} {emojis.LB_MYSTERIOUS} mysterious lootbox.\n\n'
        f'What is it? Where does it come from? Who can open it? What is love?\n'
        f'It is a mystery, my friends.\n'
        f'Time will tell, maybe. Or maybe not? Who knows. In the meantime, enjoy your troll box.'
    )

    if partner_loot:
        description = f'{description}\n\n(Luckily, their partner stole it, so they won\'t have to bother trying to open it)'

    return description


async def get_present_godly_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_omega event"""
    hunt_together = True if 'are hunting together' in message_content else False

    if hunt_together:
        user_name_search = "** and **"
        user_name_end = message_content.find(user_name_search)
        partner_name_start = user_name_end + len(user_name_search)
        partner_name_end = message_content.find("** are", partner_name_start)
        partner_name = message_content[partner_name_start:partner_name_end]
    else:
        user_name_end = message_content.find("** found and killed")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    lb_amount_end = message_content.find('**<:GODLY')
    lb_amount_start_search = f'**{user_name}** got '
    lb_amount_start = message_content.rfind(lb_amount_start_search, 0, lb_amount_end) + len(lb_amount_start_search)
    partner_loot = False
    if hunt_together and lb_amount_end - lb_amount_start > 3:
        lb_amount_start_search_partner = f'**{partner_name}** got '
        lb_amount_start = (message_content
                           .rfind(lb_amount_start_search_partner, 0, lb_amount_end)
                           + len(lb_amount_start_search_partner))
        partner_loot = True

    lb_amount = message_content[lb_amount_start:lb_amount_end].strip()

    description = (
        f'**{user_name}** found {lb_amount} {emojis.PRESENT_GODLY} GODLY present. Shiny!\n\n'
        f'This is completely warranted, and they clearly deserve that nice present more than you. I\'m sure you agree!'
    )

    if partner_loot:
        description = f'{description}\n\n(Don\'t tell them, but the present was actually for their partner lmao)'

    return description


async def get_present_godly_farm_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_omega event"""

    user_name_end = message_content.find("** plants")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    lb_amount_end = message_content.find('**<:GODLY')
    lb_amount_start_search = f'**{user_name}** got '
    lb_amount_start = message_content.rfind(lb_amount_start_search, 0, lb_amount_end) + len(lb_amount_start_search)

    lb_amount = message_content[lb_amount_start:lb_amount_end].strip()

    description = (
        f'**{user_name}** found {lb_amount} {emojis.PRESENT_GODLY} GODLY present. Shiny!\n\n'
        f'This is completely warranted, and they clearly deserve that nice present more than you. I\'m sure you agree!'
    )

    return description


async def get_present_godly_training_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_omega event"""

    user_name_end = message_content.find("** !")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    lb_amount_end = message_content.find('**<:GODLY')
    lb_amount_start_search = f'**{user_name}** got '
    lb_amount_start = message_content.rfind(lb_amount_start_search, 0, lb_amount_end) + len(lb_amount_start_search)

    lb_amount = message_content[lb_amount_start:lb_amount_end]

    description = (
        f'**{user_name}** found {lb_amount} {emojis.PRESENT_GODLY} GODLY present. Shiny!\n\n'
        f'This is completely warranted, and they clearly deserve that nice present more than you. I\'m sure you agree!'
    )

    return description


async def get_present_godly_quest_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the lb_omega event"""

    user_name_end = message_content.find("** got")
    user_name_start = message_content.rfind('**', 0, user_name_end) + 2
    user_name = message_content[user_name_start:user_name_end]

    lb_amount_end = message_content.find('**<:GODLY')
    lb_amount_start_search = f'**{user_name}** got '
    lb_amount_start = message_content.rfind(lb_amount_start_search, 0, lb_amount_end) + len(lb_amount_start_search)

    lb_amount = message_content[lb_amount_start:lb_amount_end].strip()

    description = (
        f'**{user_name}** found {lb_amount} {emojis.PRESENT_GODLY} GODLY present. Shiny!\n\n'
        f'This is completely warranted, and they clearly deserve that nice present more than you. I\'m sure you agree!'
    )

    return description


async def get_pet_epic_description(message_content: str, message: discord.Message) -> str:
    """Returns the embed description for the pet_epic event"""

    description = (
        f'**Someone** (idk, go check for yourself) got an EPIC pet while fusing!\n\n'
        f'I don\'t know what disturbing thing a "pet fusion" is supposed to be, but EPIC sounds good.'
    )

    return description