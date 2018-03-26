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
rSENTENCE = re.compile(r'^.+?\. ')
rBRACK = re.compile(r'[[(].+?[\])]')
rMDLINK = re.compile(r'(\[.*?\])\((.+?)\s".*?"\)')


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
        self.disamb_query = API + (
          'query'
          '&titles={}'
          '&prop=categories'
          '&cllimit=max'
          f"&clcategories={'|'.join(hardcoded.categories)}"
          )
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
          '&cllimit=max'
          f"&clcategories={'|'.join(hardcoded.categories)}"
          '|Category:Disambiguation_pages|Category:All_disambiguation_pages'
          )

    async def disambiguate(self, ctx: Context, content: str) -> str:
        """
        Ask the user to choose between snakes if the name they requested is ambiguous.
        If only one snake is present in a disambig page, redirect to it without asking.
        
        :param ctx: Needed to send the user a dialogue to choose a snake from.
        :param page: The disambiguation page in question.
        :return: 
        """
        def check(rxn, usr):
            if usr.id != ctx.message.author.id or rxn.message.id != msg.id:
                return False
            try:
                return int(rxn.emoji[0]) <= len(filt)
            except ValueError:
                return False
        soup = bs4.BeautifulSoup(content)
        potentials = [
          tag.get('title') for tag in soup.select('li a')
          if tag.parent.parent.parent.get('id') != 'toc'
          and tag.find_previous(id='See_also') is None
        ]
        async with self.session.get(self.disamb_query.format('|'.join(potentials))) as resp:
            batch = await resp.json()
        filt = [i['title'] for i in batch['query']['pages'].values() if 'categories' in i][:9]
        if len(filt) > 1:
            em = discord.Embed(title='Disambiguation')
            em.description = "Oh no, I can't tell which snake you wanted! Help me out by picking one of these:\n"
            em.description += ''.join(f'\n{idx}. {title}' for idx, title in enumerate(filt))
            msg = await ctx.send(embed=em)
            for i in range(len(filt)):
                await msg.add_reaction(f'{i}\u20E3')
            rxn, usr = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
            name = filt[int(rxn.emoji[0])]
        else:
            name = filt[0]
        
        async with self.session.get(self.base_query.format(name)) as pg_resp, \
                   self.session.get(self.info_query.format(name)) as if_resp:  # noqa: E127
            data = await pg_resp.json()
            info = await if_resp.json()
        
        return data, info

    async def get_rand_name(self, category: str = None) -> str:
        """
        Follow wikipedia's Special:RandomInCategory to grab the name of a random snake.
        
        :param category: Optional, the name of the category to search for a random page in. Omit for random category.
        :return: A random snek's name
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

    async def get_snek(self, ctx: Context, name: str = None) -> Dict[str, Any]:
        """
        Go online and fetch information about a snake.

        The information includes the name of the snake, a picture of the snake if applicable, and some tidbits.
        
        If "python" is given as the snake name, information about the programming language is provided instead.
        
        :param ctx: Only required for disambiguating to send the user a reaction-based dialogue
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        :return: A dict containing information about the requested snake
        """
        if name is None:
            name = await self.get_rand_name()

        async with self.session.get(self.base_query.format(name)) as pg_resp, \
                   self.session.get(self.info_query.format(name)) as if_resp:  # noqa: E127
            data = await pg_resp.json()
            info = await if_resp.json()
        pg_id = str(data['parse']['pageid'])
        pg_info = info['query']['pages'][pg_id]

        if 'categories' not in pg_info and pg_id != '23862':  # 23862 == page ID of /wiki/Python_(programming_language)
            raise BadSnake("This doesn't appear to be a snake!")

        cats = pg_info.get('categories', [])
        # i[9:] strips out 'Category:'
        if any(i['title'][9:] in ('Disambiguation pages', 'All disambiguation pages') for i in cats):
            try:
                data, info = await self.disambiguate(ctx, data['parse']['text']['*'])
            except BadSnake:
                raise
            pg_info = info['query']['pages'][str(data['parse']['pageid'])]

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
                tidbits.append(rMDLINK.sub(lambda m: f'{m[1]}({WKPD}{m[2].replace(" ", "")})', tidbit))
        try:
            img_url = pg_info['thumbnail']['source']
        except KeyError:
            img_url = None
        title = data['parse']['title']
        pg_url = f"{WKPD}/wiki/{title.replace(' ', '_')}"
        return {'🐍': (img_url, pg_url, title), 'tidbits': tidbits}

    @commands.command()
    async def get(self, ctx: Context, name: str.lower = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        if name == 'python':
            name = 'Python_(programming_language)'
        try:
            snek = await self.get_snek(ctx, name)
        except BadSnake as e:
            return await ctx.send(f'`{e}`')
        image, page, title = snek['🐍']
        embed = discord.Embed(title=title, url=page, description='\n\n • '.join(snek['tidbits']))
        if image is not None:
            embed.set_thumbnail(url=image)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
