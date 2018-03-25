# coding=utf-8
import logging
from typing import Any, Dict
import random
import aiohttp
import discord
from discord.ext.commands import AutoShardedBot, Context, command
import wikipedia

log = logging.getLogger(__name__)

SNAKE_LIST = ['cobra', 'python', 'anaconda', 'viper', 'mamba', 'taipan', 'rattle', 'garter', 'cylindrophis','colubridae']

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
        if name is None:
            name = random.choice(SNAKE_LIST)
        elif name.lower() == "python":
            name = "Python (Programming Language)"
        try:
            text = wikipedia.summary(name)
        except Exception as e:
            text = wikipedia.summary(e.options[0])
        return (name, text)

    @command(name="get")
    async def get(self, ctx: Context, name: str=None):
        """if name.lower() == "python":
            name_rechange = "Python Programming Language"
        else:
            name_rechange = name
        test = wikipedia.page(name_rechange)
        embed.add_field(name="Image", value=test.images[0], inline=False)
        return await ctx.send(embed=embed)
        """
        name, text = await self.get_snek(name)
        embed = discord.Embed(
            title=name,
            description=text,
            color=0x00ff00
            )
        await ctx.send(embed=embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!

    @command(name="snakerandom")
    async def SnakeRandom(self, ctx: Context, name: str = None):
        
        randsnake = random.choice(SNAKE_LIST)
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

        snk = random.choice(SNAKE_LIST)
        snLen = len(snk)
        p = len(name)
        result = ""
        front_back = 1
        if front_back == 1:  # so the users name is substring from the front and snake random substring from back
            ran = random.randint(1, p - 2)
            ranSnk = random.randint(1, snLen - 1)
            result = name[:ran] + snk[ranSnk:]

        return await ctx.send(result)


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")