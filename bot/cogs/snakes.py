# coding=utf-8

# This shit imports more than the USA D:
import async_timeout
import random
import difflib
import logging
import ast
import os
import urllib.parse
from io import BytesIO
from functools import partial

import aiohttp

from typing import Dict
from discord import Embed, File
from discord.ext.commands import AutoShardedBot, Context, command
from PIL import Image, ImageOps


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

# I don't think this is the best way of doing it
CARD = {
    "top": Image.open("bot/cards/card_top.png"),
    "frame": Image.open("bot/cards/card_frame.png"),
    "bottom": Image.open("bot/cards/card_bottom.png"),
    "backs": [
        Image.open(f"bot/cards/backs/{file}") for file in os.listdir("bot/cards/backs")
    ]
}


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @staticmethod
    def parse_arg(kwarg: str):
        """Return the value of a arg (needs manual assignment)"""
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
        name = name.lower()

        def format_url(text: str):
            """Get the full URL with that snake :D"""
            return BASEURL.format(urllib.parse.quote_plus(text))

        # Check if the snake name is valid
        if name in SNAKES:
            return format_url(name)

        # Get the most similar name if a match wasn't found
        return difflib.get_close_matches(name, SNAKES, n=5, cutoff=0)

    @staticmethod
    async def fetch_image(self, url: str):
        """Fetch an image, return a BytesIO object"""
        stream = BytesIO()
        async with async_timeout.timeout(10):
            async with self.session.get(url) as response:
                stream.write(await response.read())

        stream.seek(0)
        return stream

    async def get_snek(self, name: str = None, autocorrect: str = None) -> Dict[str, str]:
        """If a name is provided, this gets a specific snake. Otherwise, it gets a random snake."""

        autocorrect = self.parse_arg(autocorrect) or False

        # Special cases
        if name is None:
            name = random.choice(SNAKES)
        elif name.lower() == "python":
            return PYTHON

        url = self.snake_url(name)

        # Does some magic if the url is actually a list ^^
        if isinstance(url, list):
            if autocorrect:
                return await self.get_snek(url[0])

            return {
                "name": "Oops!",
                "info": "We can't find that snake, but here are some similar names:\n\n" + "\n".join(url).title()
            }

        # Get the content
        async with async_timeout.timeout(10):
            async with self.session.get(url) as response:
                response = await response.json()

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
    async def get(self, ctx: Context, name: str = None, autocorrect: str = None):

        content = await self.get_snek(name, autocorrect)

        embed = Embed(
            title=content["name"],
            description=content["info"][:2000],  # May consider cutting it shorter. 'Rattler' is a long one.
            color=0x7289da
        )

        if "image" in content:
            embed.set_image(url=content.get("image"))

        await ctx.send(embed=embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!

    # Cards are here :D

    @staticmethod
    def generate_card(buffer: BytesIO) -> BytesIO:
        """Generate a card from snake information"""

        snake = Image.open(buffer)

        # Get the size of the snake icon, configure the height of the image box (yes, it changes)
        icon_width = 347  # Hardcoded, not much i can do about that
        icon_height = int((icon_width / snake.width) * snake.height)
        frame_copies = icon_height // CARD['frame'].height + 1
        snake.thumbnail((icon_width, icon_height))

        # Get the dimensions of the final image
        main_height = icon_height + CARD['top'].height + CARD['bottom'].height
        main_width = CARD['frame'].width

        # Start creating the final image
        foreground = Image.new("RGBA", (main_width, main_height), (0, 0, 0, 0))
        foreground.paste(CARD['top'], (0, 0))

        # Generate the frame borders to the correct height
        for offset in range(frame_copies):
            position = (0, CARD['top'].height + offset * CARD['frame'].height)
            foreground.paste(CARD['frame'], position)

        # Add the image and bottom part of the image
        foreground.paste(snake, (36, CARD['top'].height))  # Also hardcoded :(
        foreground.paste(CARD['bottom'], (0, CARD['top'].height + icon_height))

        # Setup the background
        back = random.choice(CARD['backs'])
        back_copies = main_height // back.height + 1
        full_image = Image.new("RGBA", (main_width, main_height), (0, 0, 0, 0))

        # Generate the tiled background
        for offset in range(back_copies):
            full_image.paste(back, (16, 16 + offset * back.height))

        full_image.paste(foreground, (0, 0), foreground)

        # Get the image contents as a BufferIO object
        buffer = BytesIO()
        full_image.save(buffer, 'PNG')
        buffer.seek(0)

        return buffer

    @command()
    async def snake_card(self, ctx: Context, name: str = None, autocorrect: str = 'True'):
        content = await self.get_snek(name, autocorrect)

        stream = BytesIO()
        async with async_timeout.timeout(10):
            async with self.session.get(content['image']) as response:
                stream.write(await response.read())

        stream.seek(0)

        async with ctx.typing():
            func = partial(self.generate_card, stream)
            final_buffer = await self.bot.loop.run_in_executor(None, func)

        await ctx.send(
            f"A wild {content['name'].title()} appears!",
            file=File(final_buffer, filename=content['name'].replace(" ", "") + ".png")
        )


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
