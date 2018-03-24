# coding=utf-8
import asyncio
import logging
import random
import re
from typing import Any, Dict

import aiohttp
import bs4
import discord
import html2text
from discord.ext import commands
from discord.ext.commands import Context

from .. import hardcoded

log = logging.getLogger(__name__)

WKPD = 'https://en.wikipedia.org'
API = WKPD + '/w/api.php?format=json&redirects=1&action='
rSENTENCE = re.compile(r'^.+?\.')
rBRACK = re.compile(r'[[(].+?[\])]')
rMDLINK = re.compile(r'(\[.*?\])\((\S+?)\s".*?"\)')


class BadSnake(ValueError):
    pass


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)  # the provided session says no host is reachable
        self.h2md = html2text.HTML2Text()
        self.base_query = API + (
          'parse'
          '&page={}'
          '&prop=text|sections'
        )
        self.info_query = API + (
          'query'
          '&titles={}'
          '&prop=pageimages|categories'
          '&pithumbsize=300'
          f"&cllimit=max&clcategories={'|'.join(hardcoded.categories)}"
          )

    async def get_rand_snek(self, category: str = None):
        """
        Follow wikipedia's Special:RandomInCategory to grab the name of a random snake.
        """
        if category is None:
            category = random.choice(hardcoded.categories)
        while True:
            async with self.session.get(f"{WKPD}/wiki/Special:RandomInCategory/{category}") as resp:
                *_, name = resp.url.path.split('/')
                if 'Category:' not in name:  # Sometimes is a subcategory instead of an article
                    break
            await asyncio.sleep(1)  # hmm
        return name

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
        if name is None:
            name = await self.get_rand_snek()

        async with self.session.get(self.base_query.format(name)) as pg_resp, \
                   self.session.get(self.info_query.format(name)) as if_resp:  # noqa
            data = await pg_resp.json()
            info = await if_resp.json()

        pg_id = str(data['parse']['pageid'])
        pg_info = info['query']['pages'][pg_id]
        if 'categories' not in pg_info:
            raise BadSnake("This doesn't appear to be a snake!")
        soup = bs4.BeautifulSoup(data['parse']['text']['*'])
        tidbits = []
        for section in data['parse']['sections']:
            if sum(map(len, tidbits)) > 1500:
                break
            tag = rBRACK.sub('', str(soup.find(id=section['anchor']).find_next('p')))
            try:
                tidbit = self.h2md.handle(rSENTENCE.match(tag).group()).replace('\n', ' ')
            except AttributeError:
                pass
            else:
                tidbits.append(rMDLINK.sub(lambda m: f'{m[1]}({WKPD}{m[2]})', tidbit))
        try:
            img_url = pg_info['thumbnail']['source']
        except KeyError:
            img_url = None
        title = data['parse']['title']
        pg_url = f"{WKPD}/wiki/{title.replace(' ', '_')}"
        return {'info': (img_url, pg_url, title), 'tidbits': tidbits}

    @commands.command()
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
        except BadSnake as e:
            return await ctx.send(f'`{e}`')
        image, page, title = snek['info']
        embed = discord.Embed(title=title, url=page, description='\n\n • '.join(snek['tidbits']))
        if image is not None:
            embed.set_thumbnail(url=image)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
