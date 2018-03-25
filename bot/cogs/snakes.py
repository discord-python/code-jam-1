import logging
from typing import Any, Dict

from discord.ext.commands import AutoShardedBot, Context, command

log = logging.getLogger(__name__)
import discord

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
        

    @command()
    async def get(self, ctx: Context, *, query: str = None):
        """
        Go online and fetch information about a snake
        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.
        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """

        em = discord.Embed(title=str(query))
        em.set_footer(text='Powered by wikipedia.org')
        async with self.bot.http_session.get(f"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles={query}") as resp:
            data = await resp.json()
            data = data['query']
            em.description = (data["pages"][list(data["pages"].keys())[0]]["extract"])[:2000]
        await ctx.send(embed=em)
        

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
