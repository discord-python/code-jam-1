# coding=utf-8
import logging
from difflib import get_close_matches
from random import choice
from typing import Any, Dict

from aiohttp import ClientSession

from bs4 import BeautifulSoup

import discord
from discord.ext.commands import AutoShardedBot, Context, command

from bot.selectors import (
    ALT_IMG_SELECTOR,
    DID_YOU_KNOW_SELECTOR,
    SCIENTIFIC_NAME_SELECTOR,
    SNAKE_IMG_SELECTOR,
    SNEK_MAP_SELECTOR
)

log = logging.getLogger(__name__)

PYTHON_INFO = {
    'name': 'Python',
    'scientific-name': 'Pseudo anguis',
    'image-url': 'https://www.python.org/static/community_lopython-logo-master-v3-TM.png',
    'url': 'https://en.wikipedia.org/wiki/Python_(programming_language)',
    'map-url': 'https://ih0.redbubble.net/image.80621508.8flat,800x800,075,t.u1.jpg',
    'description': 'Python is an interpreted high-level programmlanguage '
                   'for general-purpose programming. '
                   'Created by Guido van Rossum and first released1991, '
                   'Python has a design philosophy that emphasizes creadability, '
                   'notably using significant whitespace.'
}


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def on_ready(self):
        self.session = ClientSession(loop=self.bot.loop)
        self.info_url = 'https://snake-facts.weebly.com/'
        log.info('Session created.')

        with open('./snakes.txt', encoding='utf-8') as f:
            self.sneks = f.read().split('\n')
            for i, snek in enumerate(self.sneks):
                self.sneks[i] = snek.replace('\u200b', '').replace('\ufeff', '')
        log.info('Snakes loaded.')

    def no_sneks_found(self, name: str) -> discord.Embed:
        """Helper function if the snake was not found in the directory."""
        em = discord.Embed(
            title='No snake found.',
            color=discord.Color.green()
        )

        snakes = get_close_matches(name, self.sneks)

        if snakes:
            em.description = 'Did you mean...\n'
            em.description += '\n'.join(f'`{x}`' for x in snakes)
        else:
            snakes = 'https://github.com/SharpBit/code-jam-1/blob/master/snakes.txt'
            em.description = f'No close matches found. Click [here]({snakes}) for the list of available snakes.'

        return em

    def format_info(self, data: dict, color=discord.Color.green()) -> discord.Embed:
        """Formats the info with the given data."""
        em = discord.Embed(
            title=f"{data['name']} ({data['scientific-name']})",
            description=data['description'],
            color=color,
            url=data['url']
        )

        em.set_image(url=data['image-url'])
        em.set_thumbnail(url=data['map-url'])

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
            if name not in self.sneks:
                return self.no_sneks_found(name)
        else:
            name = choice(self.sneks)

        snake = name.lower().replace(' ', '-').replace("'", '')
        url = f'{self.info_url}{snake}.html'

        async with self.session.get(url) as resp:
            info = await resp.read()
            soup = BeautifulSoup(info, 'lxml')

        for x in range(1, 7):
            try:
                img = soup.select(SNAKE_IMG_SELECTOR.format(x))[0]['src']
                break
            except IndexError:
                continue
        try:
            img = img[1:]
        except UnboundLocalError:
            img = soup.select(ALT_IMG_SELECTOR)[0]['src'][1:]

        names = soup.find('td', class_='wsite-multicol-col')
        sci_name = soup.select(SCIENTIFIC_NAME_SELECTOR)[0].text.strip()
        description_tag = soup.find(attrs={'property': {'og:description'}})

        for x in range(1, 7):
            try:
                location_map = soup.select(SNEK_MAP_SELECTOR.format(x))[0]['src']
                break
            except IndexError:
                continue

        info = {
            'name': names.h1.string,
            'scientific-name': sci_name,
            'image-url': f'{self.info_url}{img}',
            'map-url': f'{self.info_url}{location_map[1:]}',
            'description': description_tag['content'],
            'url': url
        }

        return info

    async def get_snek_fact(self) -> discord.Embed:
        """Helper function to get a snake fact."""
        page = choice(self.sneks).replace(' ', '-').replace("'", '')
        url = f'{self.info_url}{page}.html'

        async with self.session.get(url) as resp:
            response = await resp.read()
            soup = BeautifulSoup(response, 'lxml')
            fact = soup.select(DID_YOU_KNOW_SELECTOR)[0].text

        em = discord.Embed(
            title='Did you know?',
            description=fact[13:],
            color=discord.Color.green()
        )

        return em

    @command(aliases=['snakes.get', 'snakes.get()', 'get()'])
    async def get(self, ctx: Context, *, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        # Sends info about the programming language
        if name:
            if name.lower() == 'python':
                em = self.format_info(PYTHON_INFO, discord.Color.blurple())
                return await ctx.send(embed=em)
        data = await self.get_snek(name)
        # if the snake is not found
        if isinstance(data, discord.Embed):
            return await ctx.send(embed=data)
        # format the given data
        em = self.format_info(data)
        await ctx.send(embed=em)

    @command(aliases=['getsnekfact', 'snekfact()', 'get_snek_fact()'])
    async def snekfact(self, ctx: Context):
        """
        Gets a randomsnek fact from the "Did you know?" cards
        that the website has on the right hand side.
        """
        await ctx.send(embed=await self.get_snek_fact())


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
