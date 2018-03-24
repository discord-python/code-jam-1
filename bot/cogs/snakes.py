# coding=utf-8
import logging
from typing import Any, Dict
import discord
import random
import time
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
        name1 = name.lower()
        cobra = 'Cobra is the common name of various elapid snakes, most of which belonging to the genus Naja.'
        pythonidae = 'The Pythonidae, commonly known simply as pythons,\n from the Greek word python (πυθων), are\n a family of nonvenomous snakes found in Africa, Asia, and Australia.\n Among its members are some of the largest snakes in the world.\n Eight genera and 31 species are currently recognized.'


        embed = discord.Embed(
            title=name1,
            description=cobra,
            color=0x00ff00,
        )
        return await ctx.send(embed=embed)
    """
            Go online and fetch information about a snake

            This should make use of your `get_snek` method, using it to get information about a snake. This information
            should be sent back to Discord in an embed.

            :param ctx: Context object passed from discord.py
            :param name: Optional, the name of the snake to get information for - omit for a random snake
    """

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


    @command(name="snakerandom")
    async def SnakeRandom(self, ctx: Context , name: str= None):
        #snakes=['Cobra','Python','Anaconda','Black Mamba','Rattle Snake']
        randsnake=random.choice(['cobra','python','black mamba'])
        print(randsnake)
        embed = discord.Embed(
            title="Snake Random !",
            description="lets see what snake you got !",
            color=0x00ff00,
        )

        embed.add_field(name="Result", value="You got yourself a "+randsnake, inline=False)
        embed.add_field(name="Expectation", value=f"@{ctx.author} expected {name}", inline=False)

        if randsnake=="python":

            return await ctx.send("Your a lucky dude !",embed=embed)
        elif randsnake=="cobra":
            return await ctx.send("Good old cobra !",embed=embed)
        elif randsnake.startswith("blac"):
            return await ctx.send("Shiny liitle fella !",embed=embed)


    @command(name="randname")
    async def RandName(self,ctx:Context , name: str=None):
        snakes=['Cobra','Python','Anaconda','Viper','Mamba']
        snk=random.choice[snakes]
        snLen=len(snk)
        p = len(name)
        result=""
        front_back=random.randint(1,3)
        if front_back==1:#so the users name in substring from the front and snake random substring from back
            ran = random.randint(0,p-2)
            ranSnk=random.randint(2,snLen)
            result=name[ :ran] + snk[ranSnk: ]
            return await ctx.send(result)

        elif front_back==2:#so the users name in substring from the back and snake random substring from front
            ran=random.randint(2,p)
            ranSnk=random.randint(0,snLen-2)
            result = name[ran: ] + snk[ :ranSnk]
            return await ctx.send(result)





def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
