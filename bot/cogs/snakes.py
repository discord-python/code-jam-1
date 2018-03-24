# coding=utf-8
import logging
from copy import copy
from pickle import load
from random import choice
from typing import Any, Dict

from discord import Embed
from discord.ext.commands import AutoShardedBot, Context, command

from ..tools import rattle


log = logging.getLogger(__name__)
db = load(open('bot/cogs/snek.pickledb', 'rb'))  # are we going to move this db elsewhere?
SNAKE_NAMES = db.keys()  # make a list of common names for snakes, used for random snake and autocorrect
DEBUG = True
print = print if DEBUG else lambda *a, **k: None


class NoGuessError(Exception):
    def __init__(self, message='', debugdata=None):
        self.message = message
        self.debugdata = debugdata


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
                possible_misspellings = list(rattle.check_word(name, SNAKE_NAMES, threshold=0.62))  # get similars
                possible_misspellings = sorted(possible_misspellings, key=lambda x: x[0])  # sort the list
                possible_misspellings = list(reversed(possible_misspellings))  # reverse it
                '''
                just a thought, should we check if the next command request from the same person goes from a possibility
                rate from, say, 0.5 to 1.0 (50% accuracy to 100%) so that we can cache known misspellings?
                '''
                try:
                    src = await self.get_snek(possible_misspellings[0][1])  # recurse/refine
                    name = src['common name']
                except IndexError:  # no guesses on misspellings
                    raise NoGuessError(debugdata='requested = {}'.format(name))
                except ValueError:
                    raise ValueError('snek not found')

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
            print('debug: {}'.format(e.debugdata))
            await ctx.send("I'm sorry, I don't know what you requested.")

        embed = Embed(title=snek.get('common name'), description=snek.get('description'))
        # Commented out until I know what information I have to use.
        # embed.add_field(name="More Information", value="```Species | xxx\rGenus   | xxx\rFamily  | xxx```")
        embed.add_field(name=snek.get('rating'), value=await self.get_danger(snek.get('rating')), inline=True)
        embed.set_image(url=snek.get('image'))
        embed.set_footer(text="Information from Wikipedia and snakedatabase.org")
        await ctx.send(embed=embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
