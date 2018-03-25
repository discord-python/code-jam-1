# coding=utf-8
import logging
from typing import Any, Dict
import random
import wikipedia
import aiohttp
import discord
from discord.ext.commands import AutoShardedBot, Context, command

log = logging.getLogger(__name__)


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

    @command(name="get")
    async def get(self, ctx: Context, name: str = None):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://en.wikipedia.org/wiki/Cobra') as resp:
                return await ctx.send(await resp.text)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!

    @command(name="snakerandom")
    async def SnakeRandom(self, ctx: Context, name: str = None):
        # snakes=['Cobra','Python','Anaconda','Black Mamba','Rattle Snake']
        randsnake = random.choice(['cobra', 'python', 'black mamba'])
        print(randsnake)
        embed = discord.Embed(
            title="Snake Random !",
            description="lets see what snake you got !",
            color=0x00ff00,
        )

        embed.add_field(name="Result", value="You got yourself a " + randsnake, inline=False)
        embed.add_field(name="Expectation", value=f"@{ctx.author} expected {name}", inline=False)

        if randsnake == "python":

            return await ctx.send("Your a lucky dude !", embed=embed)
        elif randsnake == "cobra":
            return await ctx.send("Good old cobra !", embed=embed)
        elif randsnake.startswith("blac"):
            return await ctx.send("Shiny liitle fella !", embed=embed)

    @command(name="randname")
    async def RandName(self, ctx: Context, name: str = None):
        snakes=['cobra', 'python', 'anaconda', 'viper', 'mamba','taipan','rattle','garter','cylindrophis','colubridae']
        snk = random.choice(snakes)
        snLen = len(snk)
        p = len(name)
        result = ""
        front_back = 1
        if front_back == 1:  # so the users name is substring from the front and snake random substring from back
            ran = random.randint(1, p - 2)
            ranSnk = random.randint(1, snLen - 1)
            result = name[:ran] + snk[ranSnk:]

        return await ctx.send(result)

    @command(name="RandomName")
    async def randomName(selfself,ctx:Context, name:str= None):



def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
