# coding=utf-8
import logging
from copy import copy
from difflib import get_close_matches
from os import environ
from pickle import load
from random import choice
from typing import Any, Dict

from discord import Embed
from discord.ext.commands import AutoShardedBot, Context, command


log = logging.getLogger(__name__)
db = load(open('bot/cogs/snek.pickledb', 'rb'))  # are we going to move this db elsewhere?
SNAKE_NAMES = db.keys()  # make a list of common names for snakes, used for random snake and autocorrect
DEBUG = (environ.get('SNAKES_DEBUG', None), True)
print = print if DEBUG[-1] else lambda *a, **k: None  # -1 index is used for easy temp debug hardcode


class NoGuessError(Exception):
    def __init__(self, message='', debugdata=None):
        self.message = message
        self.debugdata = debugdata


async def check_spelling(word):
    '''
    Check the spelling of a word using difflib's get_close_matches.

    :return: Closest-matching string.
    '''
    return get_close_matches(word, SNAKE_NAMES)[0]


async def fix_margins(text, maxlength=10):
    '''
    Fixes text to be a certain length.
    
    :return: A length-fixed string.
    '''
    textlen = len(text)
    if textlen > maxlength:
        text = text[:textlen - 3] + '...'
    else:
        text = text.ljust(maxlength)
    return text


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def get_snek(self, name: str = None) -> Dict[str, Any]:
        """
        Go online and fetch information about a snake

        The information includes the name of the snake, a picture of the snake, and various other pieces of info.
        What information you get for the snake is up to you. Be creative!

        If "python" is given as the snake name, you should return information about the programming language, but with
        all the information you'd provide for a real snake. Try to have some fun with this!

        :param name: Optional, the name of the snake to get information for - omit for a random snake
        :return: A dict containing information on a snake
        """
        if name is None:  # if it's None
            name = choice(SNAKE_NAMES)  # get random key (common) name
            src = db[name]  # source of info = db[common name]
        else:
            try:
                name = name.lower()  # lowercase the name for hitting dict
                src = db[name]  # source of info = db[common name]
            except KeyError:  # if name not found...
                spellcheck = await check_spelling(name)
                if spellcheck == '':
                    raise NoGuessError(debugdata='requested = {}'.format(name))
                else:
                    src = await self.get_snek(spellcheck)

        info = copy(src)  # make a copy of the dictionary
        info['common name'] = name  # make common name key
        return info

    async def get_danger(self, level: str = None) -> str:
        """
        Returns the human-readable version of the danger level.
        :param level: The danger level of a snek
        :return: A string that is the human readable version of passed level.
        """
        return {
            '???': 'Danger unknown',
            '---': 'Nonvenomous',
            '??🐍': 'Constrictor, danger unknown',
            '🐍': 'Constrictor, considered harmless',
            '🐍🐍': 'Constrictor, harmful',
            '🐍🐍🐍': 'Constrictor, dangerous',
            '🐍🐍🐍🐍': 'Constrictor, very dangerous',
            '🐍🐍🐍🐍🐍': 'Constrictor, extremely damgerous',
            '??💀': 'Venomous, danger unknown',
            '💀': 'Venomous, considered harmless',
            '💀💀': 'Venomous, harmful',
            '💀💀💀': 'Venomous, dangerous',
            '💀💀💀💀': 'Venomous, very dangerous',
            '💀💀💀💀💀': 'Venomous, extremely dangerous.'
        }.get(level, 'Unknown')

    @command()
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """

        try:
            snek = await self.get_snek(name)
        except NoGuessError as e:
            print('debug: {0}'.format(e.debugdata))
            await ctx.send("I'm sorry, I don't know what you requested.")

        rating = snek.get('rating')
        family = fix_margins(snek.get('family'))
        common = snek.get('common name')
        uimage = snek.get('image')
        scient = fix_margins(snek.get('scientific'))
        length = fix_margins(snek.get('length'))
        spit = fix_margins(snek.get('spit'))

        # embed = Embed(title=snek.get('common name'), description=snek.get('description'))
        embed = Embed(title=snek.get('common name'))
        # Commented out until I know what information I have to use.
        embed.add_field(name="More Information", value='''```Family    | {}
Scientific | {}
Length     | {}
Spitting   | {}
```'''.format(family, scient, length, spit))
        embed.add_field(name='Threat', value=await self.get_danger(rating), inline=True)
        embed.set_image(url=uimage)
        embed.set_footer(text="Information from snakedatabase.org")
        await ctx.send(embed=embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!
    @command()
    async def speak(self, ctx: Context, text: str=None):
        """
        Takes any text passed in and snekifies it.

        :param ctx: Context from discord.py
        :param text: Optional, the text to snekify
        """

        if text is None:
            await ctx.send("I can't ssssnekify nothing!")
        else:
            await ctx.send("Sssneks ssay " + text.replace('s', 'ss'))


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
