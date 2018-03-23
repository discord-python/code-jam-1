# coding=utf-8
import json
import logging
import os
import random
from typing import Any, Dict

import aiohttp

import discord
from discord.ext.commands import AutoShardedBot, Context, command

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

    async def get_snek_qwant_json(self, snake_name):
        """
        Gets the json from Unsplash for a given snake query
        :param snake_name: name of the snake
        :return: the full JSON from the search API
        """
        url = "https://api.unsplash.com/search/photos?client_id" \
              "={0}&query={1}".format(os.environ.get("UNSPLASH_CLIENT_ID"), snake_name)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response = await response.read()
                return json.loads(response.decode("utf-8"))

    async def get_snek_image(self, name):
        """
        Gets the URL of a snake image
        :param name: name of snake
        :return: image url
        """
        json_response = await self.get_snek_qwant_json(name)
        rand = random.randint(0, 9)  # prevents returning the same image every time
        return json_response['results'][rand]['urls']['small']

    @command()
    async def get(self, ctx: Context, name: str = "python"):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        url = await self.get_snek_image(name)   # not limited to snakes - user can search anything they like
        await ctx.channel.send(
            content=ctx.message.author.mention + " Here's your snek!",
            embed=discord.Embed().set_image(url=url)
        )

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
