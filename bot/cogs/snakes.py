# coding=utf-8
import logging
from typing import Any, Dict

from discord.ext.commands import AutoShardedBot, Context, command
from discord import Embed

import aiohttp
import json
import async_timeout
import random

log = logging.getLogger(__name__)

# Probably should move these somewhere
BASEURL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=%{}&redirect=1"
PYTHON = {
    "name": "Python",
    "info": """Python is a species of programming language, \
commonly used by coding beginners and experts alike. It was first discovered \
in 1989 by Guido van Rossum in the Netherlands, and was released to the wild \
two years later. Its use of dynamic typing is one of many distinct features, \
alongside significant whitespace, heavy emphasis on readability, and, above all, \
absolutely pain-free software distribution... *sigh*"""
}
with open("bot/snakes.txt") as file:
    SNAKES = file.readlines()


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
        if name.upper() + '\n' in list(map(lambda n: n.upper(), SNAKES)):
            return encode_url(name)

        # Get a list of similar names if a match wasn't found 
        suggestions = []
        for line in SNAKES:
            if len(set(name) & set(line)) > 0.5 * len(name):
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
            name = random.choice([x.strip('\n') for x in SNAKES])

        if name.upper() == "PYTHON":
            return PYTHON

        # Get snake information
        async with aiohttp.ClientSession() as session:
            url = self.snake_url(name)
            query = await self.fetch(session, url)
            page = query["query"]["pages"]
            content = next(iter(page.values()))
            print(content)

            # WHY WOULD YOU USE DICTIONARY LITERAL IN A RETURN STATEMENT but okay lol
            return {
                "name": content["title"],
                "info": content["extract"] or "I don't know much about this snake, sorry!"
            }

    @command()
    async def get(self, ctx: Context, name: str = None):
        content = await self.get_snek(name)
        # Just a temporary thing to make sure it's working
        em = Embed()
        em.title = content["name"]
        em.description = content["info"]

        await ctx.send(embed=em)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
