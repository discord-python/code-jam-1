# coding=utf-8
import logging
from typing import Any, Dict
import random
import discord
from discord.ext.commands import AutoShardedBot, Context, command
import wikipedia

log = logging.getLogger(__name__)

SNAKE_LIST = ['cobra', 'python', 'anaconda', 'viper', 'mamba', 'taipan', 'rattle', 'garter', 'cylindrophis',
              'colubridae']


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
            name = "Python(Programming Language)"

        try:
            text = wikipedia.summary(name, sentences=2)
        except Exception as e:
            text = wikipedia.summary(e.options[0], sentences=2)
        return (name, text)

    @command(name="get")
    async def get(self, ctx: Context, name: str = None):

        name, text = await self.get_snek(name)
        for_image = ''
        if name == "Python(Programming Language)":
            for_image = 'https://raw.githubusercontent.com/discord-python/branding/master/logos/logo_full.png'
            embed = discord.Embed(title="Programming !!", color=0x00ff00)
            embed.add_field(name=name, value=text)
            embed.set_image(url=for_image)
            await ctx.send(embed=embed)
        else:
            webpage = wikipedia.WikipediaPage(name)
            for_image = webpage.images[0]
            embed = discord.Embed(title="Snake !!", color=0x00ff00)
            embed.add_field(name=name, value=text)
            embed.set_image(url=for_image)
            await ctx.send(embed=embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!

    @command(name="snakerandom")
    async def snake_random(self, ctx: Context, name: str = None):

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
            return await ctx.send("You're a lucky dude ! ", embed=embed)
        elif randsnake == "cobra":
            return await ctx.send("Good old cobra !", embed=embed)
        elif randsnake.startswith("blac"):
            return await ctx.send("Shiny liitle fella !", embed=embed)

    @command(name="randname")#this name generator randomply slics strings and joins them
    async def Random_name(self, ctx: Context, name: str = None):

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

    @command(name="namegen")#this name generator looks at vowels
    async def name_generator(self, ctx: Context, name: str = None):
        snk = random.choice(SNAKE_LIST)
        s = name
        str1 = ""
        str2 = ""
        for i in s:
            str1 = i + str1

        index2 = 0
        index1 = 0
        for index, char in enumerate(str1):
            if char in 'aeiou':

                index1 = index
                break
            
        name_index = len(s) - index1

        name_sub_string = s[:name_index-1]

        snake = snk
        for i in snake:
            str2 = i + str2


        for index, char in enumerate(str2):
            if char in 'aeiou':

                index2 = index
                break

        sub_string_index = len(snake) - index2
        snake_sub_string = snake[1:sub_string_index]

        return await ctx.send(name_sub_string+snake_sub_string)

def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
