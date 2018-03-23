# coding=utf-8
import logging
from typing import Any, Dict

from discord.ext.commands import AutoShardedBot, Context, command

import aiohttp
import json
import async_timeout
import random

log = logging.getLogger(__name__)

# Probably should move these somewhere
BASEURL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%{}"
SNAKE_FILE = "bot/snakes.txt"


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @staticmethod
    def snake_url(name) -> str:
        """Get the URL of a snake"""
        
        def encode_url(text):
            """Encode a string to URL-friendly format"""
            return BASEURL.format("%".join("{:02x}".format(ord(c)) for c in text))

        # Check if the snake name is known
        with open(SNAKE_FILE) as snakes:
            if name + '\n' in snakes:
                return encode_url(name)

        # Get a list of similar names if a match wasn't found 
        suggestions = []
        with open(SNAKE_FILE) as file:
            for line in file:
                if len(set(name.replace(' ', '')) & set(line.replace(' ', '').strip('\n'))) > 5:
                    suggestions.append(line.strip('\n'))

        return encode_url(random.choice(suggestions))

    async def fetch(self, session, url):
        """Fetch the contents of a URL as text"""
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.json()

    async def get_snek(self, name: str = None) -> Dict[str, Any]:
        """Get a snake with a given name, or otherwise randomly"""
        if name is None:
            name = random.choice([x.strip('\n') for x in open(SNAKE_FILE).readlines()])

        # Get snake information
        async with aiohttp.ClientSession() as session:
            url = self.snake_url(name)
            query = await self.fetch(session, url)
            page = query["query"]["pages"]
            content = next(iter(page.values()))

            # WHY WOULD YOU USE DICTIONARY LITERAL IN A RETURN STATEMENT but okay lol
            return {
                "name": content["title"],
                "info": content["extract"] or "I don't know much about this snake, sorry!"
            }

    @command()
    async def get(self, ctx: Context, name: str = None):
        content = await self.get_snek(name)
        # Just a temporary thing to make sure it's working
        await ctx.send(content)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
