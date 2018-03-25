# coding=utf-8

import async_timeout
import random
import difflib
import logging
import urllib.parse
import ast

import aiohttp

from typing import Dict, List
from discord import Embed
from discord.ext.commands import AutoShardedBot, Context, command


log = logging.getLogger(__name__)

# Probably should move these somewhere

WIKI = "https://en.wikipedia.org/w/api.php?"
BASEURL = WIKI + "format=json&action=query&prop=extracts|pageimages&exintro=&explaintext=&titles={}&redirects=1"
FAILIMAGE = "http://i.imgur.com/HtIPyLy.png/beep"
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
    def parse_kwarg(kwarg: str):
        """Return the value of a kwarg (needs manual assignment)"""
        try:
            items = kwarg.split("=")
            value = items[1]
        except (IndexError, AttributeError):
            value = kwarg

        try:
            parsed = ast.literal_eval(value)
        except (NameError, ValueError):
            parsed = value

        return parsed

    @staticmethod
    def snake_url(name: str):
        """Get the URL of a snake"""

        def format_url(text: str):
            """Get the full URL with that snake :D"""
            return BASEURL.format(urllib.parse.quote_plus(text))

        # Check if the snake name is valid
        if name.upper() in [name.upper() for name in SNAKES]:
            return format_url(name)

        # Get the most similar name if a match wasn't found
        return difflib.get_close_matches(name, SNAKES, n=5, cutoff=0)

    @staticmethod
    async def fetch(session, url: str):
        """Fetch the contents of a URL as a json"""
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.json()

    async def get_snek(self, name: str = None, autocorrect: str = None, details: List[str] = None) -> Dict[str, str]:
        """If a name is provided, this gets a specific snake. Otherwise, it gets a random snake."""

        autocorrect = self.parse_kwarg(autocorrect) or False
        details = self.parse_kwarg(details) or []

        if name is None:
            name = random.choice(SNAKES)

        if name.upper() == "PYTHON":
            return PYTHON

        # Get snake information
        async with aiohttp.ClientSession() as session:
            url = self.snake_url(name)

            if isinstance(url, list):
                if autocorrect:
                    return await self.get_snek(url[0])

                return {
                    "name": "Oops!",
                    "info": "We couldn't find that snake, but here are some with similar names:\n\n" + "\n".join(url),
                }

            # Get the content
            response = await self.fetch(session, url)
            page = response["query"]["pages"]
            content = next(iter(page.values()))

            # Parse the full-res image from the thumbnail
            thumb = content.get("thumbnail", {}).get("source", FAILIMAGE)
            image = "/".join(thumb.replace("thumb/", "").split("/")[:-1])

            return {
                "name": content["title"],
                "info": content.get("extract", "I don't know about that snake!"),
                "image": image
            }

    @command()
    async def get(self, ctx: Context, name: str = None, autocorrect: str = None, details: str = None):

        content = await self.get_snek(name, autocorrect, details)
        # Just a temporary thing to make sure it's working
        embed = Embed(
            title=content["name"],
            description=content["info"][:1970],
            color=0x7289da
        )

        if "image" in content:
            embed.set_image(url=content.get("image"))

        await ctx.send(embed=embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
