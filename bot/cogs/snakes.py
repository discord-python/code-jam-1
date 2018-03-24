# coding=utf-8
import logging
import aiohttp
import random
from bs4 import BeautifulSoup
from typing import Any, Dict
from discord.ext.commands import AutoShardedBot, Context, command

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """
    embed = {}
    python_info = '''
                    Python (Programming Language)
                    \n
                    Python is powerful... and fast;\n
                    plays well with others;\n
                    runs everywhere;\n
                    is friendly & easy to learn;\n
                    is Open.
                    -------------------------------
                    Created by: Guido Van Rossum \n 
                    Founded: 20th of February, 1991 \n
                    Official website: https://python.org
                '''

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
        '''
        site = 'https://en.wikipedia.org/wiki/List_of_snakes_by_common_name'
        async with aiohttp.ClientSession() as session:
            async with session.get(site) as resp:
                text = await resp.read()
                snake = name
                soup = BeautifulSoup(text, 'lxml')
                soup.find(snake)
        '''

        if str(name).lower() == 'python':
                '''
                Python (Programming Language)
                \n
                Python is powerful... and fast;\n
                plays well with others;\n
                runs everywhere;\n
                is friendly & easy to learn;\n
                is Open.
                -------------------------------
                Created by: Guido Van Rossum \n 
                Founded: 20th of February, 1991 \n
                Official website: https://python.org
                '''
                name = self.python_info
        return name

    @command()
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        # await ctx.send(BeautifulSoup(text, 'lxml').find("title"))
        await ctx.send(await self.get_snek(name))

        # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
