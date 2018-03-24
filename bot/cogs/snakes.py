# coding=utf-8
import logging
from difflib import get_close_matches
from random import choice
from typing import Any, Dict

from bs4 import BeautifulSoup

import discord
from discord.ext.commands import AutoShardedBot, Context, command

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    def no_sneks_found(self, name):
        '''Helper function if the snake was not found in the directory.'''
        em = discord.Embed(
            title='No snake found.',
            color=discord.Color.green()
        )
        snakes = get_close_matches(name, self.bot.sneks)
        if snakes:
            em.description = 'Did you mean...\n'
            em.description += '\n'.join(f'`{x}`' for x in snakes)
        else:
            snakes = 'https://github.com/SharpBit/code-jam-1/blob/master/snakes.txt'
            em.description = f'Click [here]({snakes}) for the list of available snakes.'
        return em

    def format_info(self, data):
        '''Formats the info with the given data'''
        em = discord.Embed(
            title=f"{data['name']} ({data['scientific-name']})",
            description='Nothing yet.',
            color=discord.Color.green()
        )
        em.set_thumbnail(url=data['image-url'])
        em.set_footer(text='Bot by SharpBit and Volcyy')

        return em

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
        if name:
            if name not in self.bot.sneks:
                return self.no_sneks_found(name)
        else:
            name = choice(self.bot.sneks)
        snake = name.lower().replace(' ', '-')
        url = f'{self.bot.info_url}{snake}.html'
        async with self.bot.session.get(url) as resp:
            info = await resp.read()
            soup = BeautifulSoup(info, 'lxml')
        img = soup.find(attrs={'property': {'og:image'}})['content']
        names = soup.find('td', class_='wsite-multicol-col')
        info = {
            'name': names.h1.string,
            'scientific-name': names.h2.string,
            'image-url': img
        }

        return info

    @command()
    async def get(self, ctx: Context, *, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        data = await self.get_snek(name)
        # if the snake is not found
        if isinstance(data, discord.Embed):
            return await ctx.send(embed=data)
        # format the given data
        em = self.format_info(data)
        await ctx.send(embed=em)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
