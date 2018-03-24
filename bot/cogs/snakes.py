# coding=utf-8
import logging
from typing import Any, Dict

from googleapiclient.discovery import build
from discord.ext.commands import AutoShardedBot, Context, command
from discord import Embed

import aiohttp
import json
import async_timeout
import random
import difflib

log = logging.getLogger(__name__)

# Probably should move these somewhere
BASEURL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts|pageimages&exintro=&explaintext=&titles=%{}&redirects=1"
PYTHON = {
    "name": "Python",
    "info": """Python is a species of programming language, \
commonly used by coding beginners and experts alike. It was first discovered \
in 1989 by Guido van Rossum in the Netherlands, and was released to the wild \
two years later. Its use of dynamic typing is one of many distinct features, \
alongside significant whitespace, heavy emphasis on readability, and, above all, \
absolutely pain-free software distribution... *sigh*""",
    "image": "https://www.python.org/static/community_logos/python-logo-master-v3-TM-flattened.png"
}
with open("bot/snakes.txt") as file:
    SNAKES = list(map(lambda ln: ln.strip('\n'), file.readlines()))


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
        if name.upper() in list(map(lambda n: n.upper(), SNAKES)):
            return encode_url(name)

        # Get the most similar name if a match wasn't found
        return encode_url(difflib.get_close_matches(name, SNAKES, n=1, cutoff=0)[0])

    @staticmethod
    async def fetch(session, url):
        """Fetch the contents of a URL as a json"""
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.json()

    async def get_snek(self, name: str = None) -> Dict[str, str]:
        """Get a snake with a given name, or otherwise randomly"""
        if name is None:
            name = random.choice([x.strip('\n') for x in SNAKES])
            
        elif name.upper() == "PYTHON":
            return PYTHON

        # Get snake information
        async with aiohttp.ClientSession() as session:
            url = self.snake_url(name)

            # Get the 
            response = await self.fetch(session, url)
            page = response["query"]["pages"]
            content = next(iter(page.values()))

            # Parse the full-res image from the thumbnail
            thumb = content.get("thumbnail", {}).get("source", "http://i.imgur.com/HtIPyLy.png/beep")
            image = "/".join(thumb.replace("thumb/", "").split("/")[:-1])
            
            # WHY WOULD YOU USE DICTIONARY LITERAL IN A RETURN STATEMENT but okay lol
            return {
                "name": content["title"],
                "info": content.get("extract", "") or "I don't know about that snake!",
                "image": image
            }

    @command()
    async def get(self, ctx: Context, name: str = None):
        content = await self.get_snek(name)
        # Just a temporary thing to make sure it's working
        em = Embed()
        em.title = content["name"]
        em.description = content["info"][:1970] + "\n\nPS. If the image is a fucking map, blame wikipedia. -Somejuan"
        em.set_image(url=content["image"])

        await ctx.send(embed=em)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
