# coding=utf-8
import logging
import re

import aiohttp
import bs4
import discord
import html2text
from discord.ext import commands

log = logging.getLogger(__name__)
API = 'http://en.wikipedia.org/w/api.php?format=json&redirects=1&action='

rSENTENCE = re.compile(r'^.+?\.')
rBRACK = re.compile(r'[[(].+?[\])]')


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot):
        self.bot = bot
        self.aexec = bot.loop.run_in_executor
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.h2md = html2text.HTML2Text()  # TODO: use
        self.base_query = API + 'parse&prop=text&page={}'
        self.secs_query = API + 'parse&prop=sections&page={}'
        self.img_query = API + 'query&titles={}&prop=pageimages&pithumbsize=300'

    async def get_snek(self, name=None):
        """
        Go online and fetch information about a snake

        The information includes the name of the snake, a picture of the snake, and various other pieces of info.
        What information you get for the snake is up to you. Be creative!

        If "python" is given as the snake name, you should return information about the programming language, but with
        all the information you'd provide for a real snake. Try to have some fun with this!

        :param name: Optional, the name of the snake to get information for - omit for a random snake
        :return: A dict containing information on a snake
        """
        # TODO: Random will be done by fetching from Special:RandomInCategory/Venomous_snakes, or something
        async with self.session.get(self.base_query.format(name)) as pg_resp, \
                   self.session.get(self.secs_query.format(name)) as sc_resp, \
                   self.session.get(self.img_query.format(name)) as img_resp:
            data = await pg_resp.json()
            secs = await sc_resp.json()
            img = await img_resp.json()
        tidbits = []
        soup = bs4.BeautifulSoup(data['parse']['text']['*'])
        for section in secs['parse']['sections']:
            for tag in await self.aexec(None, soup.find(id=section['anchor']).find_all_next):  # FIXME: inefficient...?
                if tag.name == 'p':
                    try:
                        tidbits.append(rBRACK.sub('', rSENTENCE.match(tag.text)[0]))
                    except TypeError:
                        pass
                    break
        try:
            pgid = str(data['parse']['pageid'])
            imglink = img['query']['pages'][pgid]['thumbnail']['source']
        except KeyError:
            imglink = ''
        return {'image': imglink, 'tidbits': tidbits}

    @commands.command()
    async def get(self, ctx, name: str.title = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        d = await self.get_snek(name)
        embed = discord.Embed(description='\n\n • '.join(d['tidbits']))
        embed.set_thumbnail(url=d['image'])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
