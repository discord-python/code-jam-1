# coding=utf-8
import logging
from difflib import get_close_matches
from random import choice
from typing import Any, Dict

from bs4 import BeautifulSoup

import discord
from discord.ext.commands import AutoShardedBot, Context, command

log = logging.getLogger(__name__)

# sometimes it's the 2nd div after 2nd td, sometimes it's the 3rd div.
# either way, it's returning `None`, so then info url + None = info url
# which is what the thumbnail url is currently.
SNEK_MAP_SELECTOR = (
    "#wsite-content > div:nth-of-type(2) > div > div > table > "
    "tbody > tr > td:nth-of-type(2) > div:nth-of-type(3) > div > a > img"
)

SCIENTIFIC_NAME_SELECTOR = (
    "#wsite-content > div:nth-of-type(1) > div > div > "
    "table > tbody > tr > td:nth-of-type(1) > div:nth-of-type(2)"
)

DID_YOU_KNOW_SELECTOR = (
    '#wsite-content > div:nth-of-type(2) > div > div > table > '
    'tbody > tr > td:nth-of-type(2) > div:nth-of-type(1)'
)


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
            em.description = f'No close matches found. Click [here]({snakes}) for the list of available snakes.'

        return em

    def format_info(self, data):
        '''Formats the info with the given data.'''
        em = discord.Embed(
            title=f"{data['name']} ({data['scientific-name']})",
            description=data['description'],
            color=discord.Color.green(),
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
        sci_name = soup.select(SCIENTIFIC_NAME_SELECTOR)[0].text.strip()
        location_map = soup.select(SNEK_MAP_SELECTOR)[0]['src']
        description_tag = soup.find(attrs={'property': {'og:description'}})

        info = {
            'name': names.h1.string,
            'scientific-name': sci_name,
            'image-url': img,
            'map-url': f'{self.bot.info_url}{location_map}',
            'description': description_tag['content'],
            'url': url
        }

        return info

    async def get_snek_fact(self):
        '''Helper function to get a snake fact.'''
        page = choice(self.bot.sneks).replace(' ', '-')
        url = f'{self.bot.info_url}{page}.html'

        async with self.bot.session.get(url) as resp:
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
        data = await self.get_snek(name)
        # if the snake is not found
        if isinstance(data, discord.Embed):
            return await ctx.send(embed=data)
        # format the given data
        em = self.format_info(data)
        await ctx.send(embed=em)

    @command(aliases=['getsnekfact', 'snekfact()', 'get_snek_fact()'])
    async def snekfact(self, ctx: Context):
        '''
        Gets a randomsnek fact from the "Did you know?" cards
        that the website has on the right hand side.
        '''
        await ctx.send(embed=await self.get_snek_fact())


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
