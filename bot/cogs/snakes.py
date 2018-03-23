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
from googleapiclient.discovery import build

log = logging.getLogger(__name__)

# Probably should move these somewhere
<<<<<<< HEAD
BASEURL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles={}&redirect=1"
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
    SNAKES = file.readlines()
=======
BASEURL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles={}"
SNAKE_FILE = "bot/snakes.txt"
>>>>>>> 47e03d6cd928a3bb91a1310ee04cf855c8bef834


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    @staticmethod
    def merge_dic(*args, all_iter=True):
        final = {}
        
        for dic in args:
            for k, v in dic.items():
                
                if k in final.keys():
                    if isinstance(final[k], list):
                        final[k].append(v)
                    else:
                        final[k] = [final[k], v]
                        
                elif k not in final.keys() and all_iter:
                    final[k] = [v]
                else:
                    final[k] = v
                    
        return final

<<<<<<< HEAD
    def image(self, name):
        service = build("customsearch", "v1", developerKey="API")
        res = service.cse().list(
            q=name,
            cx='ENGINE',
=======
    def iamge(self, name):
        service = build("customsearch", "v1", developerKey="AIzaSyBb1UN8_hETbwylEjBlmLudPTCB7Oy_UuM")

        res = service.cse().list(
            q=name,
            cx='002819837506601299516:4u9m7sepc8w',
>>>>>>> 47e03d6cd928a3bb91a1310ee04cf855c8bef834
            searchType='image',
            num=10,
            safe='off'
        ).execute()
        
        return random.choice(self.merge_dic(*res['items'])['link'])

    @staticmethod
    def snake_url(name) -> str:
        """Get the URL of a snake"""

        def encode_url(text):
            """Encode a string to URL-friendly format"""
            return BASEURL.format(text.replace(' ', '%20').replace("'", '%27'))

        # Check if the snake name is known
        if name.upper() + '\n' in list(map(lambda n: n.upper(), SNAKES)):
            return encode_url(name)

        # Get a list of similar names if a match wasn't found
        return encode_url(difflib.get_close_matches(name, [x.strip('\n') for x in SNAKES], n=1)[0])

    @staticmethod
    async def fetch(session, url):
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
            response = await self.fetch(session, url)
            page = response["query"]["pages"]
            content = next(iter(page.values()))

            # WHY WOULD YOU USE DICTIONARY LITERAL IN A RETURN STATEMENT but okay lol
            return {
                "name": content["title"],
                "info": str(content["extract"]) + '\n' + str(response['query'] + url),
                "image": self.image(name)
            }

    @command()
    async def get(self, ctx: Context, name: str = None):
        content = await self.get_snek(name)
        # Just a temporary thing to make sure it's working
        em = Embed()
        em.title = content["name"]
        em.description = content["info"]
        em.set_image(url=content["image"])

        await ctx.send(embed=em)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
