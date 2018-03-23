# coding=utf-8
import logging
from typing import Any, Dict
import aiohttp
import async_timeout
import pprint

from discord.ext.commands import AutoShardedBot, Context, command
from discord import Embed

log = logging.getLogger(__name__)


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

    @command()
    async def get(self, ctx: Context, name: str = "Vipera berus"):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        https://en.wikipedia.org/w/api.php?action=query&titles=Vipera_berus&prop=extracts&exsentences=2&explaintext=1&format=json
        """
        snake_embed = Embed(color=ctx.me.color, title="SNAKE")
        name = name.replace(" ", "_")

        text_params = {'action': 'query',
                       'titles': name,
                       'prop': 'extracts',
                       'exsentences': '2',
                       'explaintext': '1',
                       'format': 'json'}

        image_name_params = {'action': 'query',
                             'titles': name,
                             'prop': 'images',
                             'imlimit': '1',
                             'format': 'json'}

        async with aiohttp.ClientSession(headers={'User-Agent': 'DevBot v.10'}) as cs:
            async with async_timeout.timeout(20):
                async with cs.get("https://en.wikipedia.org/w/api.php", params=text_params) as r:
                    text_json = await r.json()
                async with cs.get("https://en.wikipedia.org/w/api.php", params=image_name_params) as r:
                    image_name_json = await r.json()

        # snake_image = "https://pbs.twimg.com/profile_images/662615956670144512/dqsVK6Nw_400x400.jpg"

        page_id = list(text_json['query']['pages'].keys())[0]
        image_id = image_name_json['query']['pages'][page_id]['images'][0]['title']

        image_url_params = {'action': 'query',
                            'titles': image_id,
                            'prop': 'imageinfo',
                            'iiprop': 'url',
                            'format': 'json'}

        async with aiohttp.ClientSession(headers={'User-Agent': 'DevBot v.10'}) as cs:
            async with async_timeout.timeout(20):
                async with cs.get("https://en.wikipedia.org/w/api.php", params=image_url_params) as r:
                    image_url_json = await r.json()

        snake_image_id = list(image_url_json['query']['pages'].keys())[0]
        snake_image = image_url_json['query']['pages'][snake_image_id]['imageinfo'][0]['url']

        snake_embed.add_field(name=name, value=text_json['query']['pages'][page_id]['extract'])
        snake_embed.set_thumbnail(url=snake_image)

        await ctx.send(embed=snake_embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
