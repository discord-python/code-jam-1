# coding=utf-8
import logging
from typing import Any, Dict

from discord.ext.commands import AutoShardedBot, Context, command

import aiohttp
import ast
import async_timeout
import random

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @staticmethod
    def snake_url(name) -> str:
        BASEURL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles={}"
        with open('snakes.txt') as s:
            if name + '\n' in s:
                return BASEURL.format("%".join("{:02x}".format(ord(c)) for c in name))
        did_you_mean = []
        with open('snakes.txt') as f:
            for line in f:
                if len(set(name.replaceI(' ', '')) & set(line.replace(' ', '')[:-2])) > 5:
                    did_you_mean.append(line[:-2])
        return BASEURL.format("%".join("{:02x}".format(ord(c)) for c in random.choice(did_you_mean)))

    async def fetch(self, session, url):
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.text()

    async def get_snek(self, name: str = None) -> Dict[str, Any]:
        if name is None:
            name = random.choice([x[-2] for x in open('snakes.txt').readlines()])
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, self.snake_url(name))
            html_to_dic = ast.literal_eval(html)
            return {
                "snake name": html_to_dic["title"],
                "snake info": html_to_dic["extract"]
            }

    @command()
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
