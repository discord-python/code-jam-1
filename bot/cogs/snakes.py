# coding=utf-8
import logging
from typing import Any, Dict
import aiohttp
import async_timeout
import random
import asyncio
import pprint

from discord.ext.commands import AutoShardedBot, Context, command
from discord import Embed

log = logging.getLogger(__name__)

SNEKFILE = 'bot/cogs/data/quote.txt'

FIRST_EMOJI = "💉"
SECOND_EMOJI = "💊"
THIRD_EMOJI = "🌡️"
FOURTH_EMOJI = "☠️"
FIFTH_EMOJI = "⚗️"

snakelist = []


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def cache_snakelist(self):
        global snakelist
        snakelist = await self.get_snake_list()

    async def get_wiki_json(self, params):
        async with aiohttp.ClientSession(headers={'User-Agent': 'DevBot v.10'}) as cs:
            async with async_timeout.timeout(20):
                async with cs.get("https://en.wikipedia.org/w/api.php", params=params) as r:
                    log.info(f"{r.url}: {r.status}: {r.reason}")
                    return await r.json()

    async def cont_query(self, params):
        last_continue = {}

        while True:
            req = params.copy()
            req.update(last_continue)

            request = await self.get_wiki_json(req)

            if 'query' not in request:
                break

            pages = request['query']['pages']['13205433']['links']
            yield pages

            if 'continue' not in request:
                break

            last_continue = request['continue']

    async def get_snake_list(self):
        ambiguous = ["(disambiguation)", "Wikipedia:", "Help:", "Category:"]

        snake_list = []
        result = self.cont_query(
            {'action': 'query', 'titles': 'list_of_snakes_by_common_name', 'prop': 'links', 'format': 'json'})
        async for dicks in result:
            listed = dicks
            for item in listed:
                if not any(s in item['title'] for s in ambiguous):
                    snake_list.append(item['title'])

        return snake_list

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
        snake_name = name
        name = name.replace(" ", "_")  # sanitize name

        text_params = {'action': 'query',
                       'titles': name,
                       'prop': 'extracts',
                       'exsentences': '2',
                       'explaintext': '1',
                       'autosuggest': '1',
                       'redirects': '1',
                       'format': 'json'}

        image_name_params = {'action': 'query',
                             'titles': name,
                             'prop': 'images',
                             'redirects': '1',
                             'autosuggest': '1',
                             'imlimit': '1',
                             'format': 'json'}

        text_json = await self.get_wiki_json(text_params)
        image_name_json = await self.get_wiki_json(image_name_params)
        snake_image = "https://pbs.twimg.com/profile_images/662615956670144512/dqsVK6Nw_400x400.jpg"

        page_id = list(text_json['query']['pages'].keys())[0]
        if page_id == "-1":  # No entry on the wiki
            snake_dict = {"name": name,
                          "snake_text": "You call that a snake?\nTHIS is a snake!",
                          "snake_image": snake_image}
            return snake_dict

        image_id = image_name_json['query']['pages'][page_id]['images'][0]['title']

        image_url_params = {'action': 'query',
                            'titles': image_id,
                            'prop': 'imageinfo',
                            'redirects': '1',
                            'autosuggest': '1',
                            'iiprop': 'url',
                            'format': 'json'}

        image_url_json = await self.get_wiki_json(image_url_params)

        snake_image_id = list(image_url_json['query']['pages'].keys())[0]
        snake_image = image_url_json['query']['pages'][snake_image_id]['imageinfo'][0]['url']
        snake_text = text_json['query']['pages'][page_id]['extract']

        snake_dict = {"name": snake_name, "snake_text": snake_text, "snake_image": snake_image}
        return snake_dict

    @command()
    async def get(self, ctx: Context, name: str = None):
        global snakelist
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        if name is None:
            name = random.choice(snakelist)
        elif name == "snakes on a plane":
            await ctx.send("https://media.giphy.com/media/5xtDartXnQbcW5CfM64/giphy.gif")
        elif name == "python":
            with open(SNEKFILE, 'r') as file:
                text = file.read()
                snake_embed = Embed(color=ctx.me.color, title="SNEK")
                snake_embed.add_field(name="Python", value=f"*{text}*")
                snake_embed.set_thumbnail(url="http://www.pngall.com/wp-content/uploads/2016/05/Python-Logo-Free-PNG-Image.png")
                await ctx.send(embed=snake_embed)

        snake = await self.get_snek(name)
        snake_embed = Embed(color=ctx.me.color, title="SNEK")
        snake_embed.add_field(name=snake['name'], value=snake['snake_text'])
        snake_embed.set_thumbnail(url=snake['snake_image'])
        await ctx.send(embed=snake_embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
    bot.loop.create_task(Snakes(bot).cache_snakelist())