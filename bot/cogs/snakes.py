# coding=utf-8

import json
import async_timeout
import random
import difflib
import logging
import urllib

import aiohttp

from typing import Dict
from discord import Embed
from discord.ext.commands import AutoShardedBot, Context, command


log = logging.getLogger(__name__)

# Probably should move these somewhere

WIKI = "https://en.wikipedia.org/w/api.php?"
BASEURL = WIKI + "format=json&action=query&prop=extracts|pageimages&exintro=&explaintext=&titles={}&redirects=1"
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
with open("bot/snakes.txt") as f:
    SNAKES = [line.strip() for line in f.readlines()]


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @staticmethod
    def snake_url(name: str) -> str:
        """Get the URL of a snake"""

        def encode_url(text):
            """Encode a string to URL-friendly format"""
            return BASEURL.format(urllib.parse.quote_plus(text))

        # Check if the snake name is valid
        if name.upper() in [name.upper() for name in SNAKES]:
            return encode_url(name)

        # Get the most similar name if a match wasn't found
        return encode_url(difflib.get_close_matches(name, SNAKES, n=1, cutoff=0)[0])

    @staticmethod
    async def fetch(session, url: str):
        """Fetch the contents of a URL as a json"""
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.json()

    async def get_snek(self, name: str = None) -> Dict[str, str]:
        """If a name is provided, this gets a specific snake. Otherwise, it gets a random snake."""
        if name is None:
            name = random.choice(SNAKES)
            
        if name.upper() == "PYTHON":
            return PYTHON

        # Get snake information
        async with aiohttp.ClientSession() as session:
            url = self.snake_url(name)

            # Get the content
            response = await self.fetch(session, url)
            page = response["query"]["pages"]
            content = next(iter(page.values()))

            # Parse the full-res image from the thumbnail
            thumb = content.get("thumbnail", {}).get("source", "http://i.imgur.com/HtIPyLy.png/beep")
            image = "/".join(thumb.replace("thumb/", "").split("/")[:-1])

            return {
                "name": content["title"],
                "info": content.get("extract", "I don't know about that snake!"),
                "image": image
            }

    @command()
    async def get(self, ctx: Context, name: str = None):
        content = await self.get_snek(name)
        # Just a temporary thing to make sure it's working
        embed = Embed(
            title = content["name"],
            description = content["info"][:1970] + "\n\nPS. If the image is a fucking map, blame wikipedia. -Somejuan",
        )
        embed.set_image(url=content["image"])

        await ctx.send(embed=embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
