# coding=utf-8
import logging
from typing import Any, Dict

import discord
import random
import aiohttp
import json
from bs4 import BeautifulSoup
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

        # Getting the summary

        async with aiohttp.ClientSession() as session:
            async with session.get('https://en.wikipedia.org/w/api.php?action=parse&format=json&page=' + name + '&section=1') as resp:
                text_data = await resp.json()
                text = json.loads(text_data)
                html = text["text"]["*"]
                soup = BeautifulSoup(html)
                summary = soup.find('p')

        # Getting the image

        async with aiohttp.ClientSession() as session:
            async with session.get('https://en.wikipedia.org/w/api.php?format=json&action=query&titles=' + name + '&prop=pageimages&pithumbsize=300') as resp:
                image_data = await resp.json()
                image = json.loads(image_data)
                url = image["thumbnail"]["source"]

        return {'summary': summary, 'url': url}
    @command()
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """

        data = await self.get_snek(name)
        await ctx.send(data)

    # The snake moult command

    @command()
    async def moult(self, ctx: Context):
        await ctx.send("sssss... moulting in progress...")
        green = discord.utils.get(ctx.guild.roles, name="Green Skin")
        black = discord.utils.get(ctx.guild.roles, name="Black Skin")
        yellow = discord.utils.get(ctx.guild.roles, name="Yellow Skin")
        await ctx.guild.me.remove_roles()
        await ctx.guild.me.add_roles(random.choice(green, black, yellow))
        await ctx.send("sssss... and now you can't see me...")

def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
