# coding=utf-8
import aiohttp
import asyncio
import logging
import random
from bs4 import BeautifulSoup
from typing import Any, Dict

# from discord import Embed, Reaction, Member
import discord
from discord.ext.commands import AutoShardedBot, Context, command

log = logging.getLogger(__name__)

class Snakes:
    """
    Snake-related commands
    """
    python_info = '''
        Python (Programming Language)
        \n
        Python is powerful... and fast;\n
        plays well with others;\n
        runs everywhere;\n
        is friendly & easy to learn;\n
        is Open-Source.
        -------------------------------
        Created by: Guido Van Rossum \n
        Founded: 20th of February, 1991 \n
        Official website: https://python.org
        '''

    def __init__(self, bot: AutoShardedBot):
        self.inputs = []
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

        if name.lower() == 'python':
            name = self.python_info

        return name

    @command()
    async def get(self, ctx: Context, name: str = None, ):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """

        site = 'https://en.wikipedia.org/wiki/' + name
        async with aiohttp.ClientSession() as session:
            async with session.get(site) as resp:
                text = await resp.text()
                soup = BeautifulSoup(text, 'lxml')
                title = soup.find('h1').text
                description = soup.find('p').text
                table = soup.find('table').text
                list(table)
                table = table[120:]
                table = ''.join(table)
                description = description + '\n' + table
                em = discord.Embed(title=title, description=description)

        if name.lower() == 'python':
            await ctx.send(await self.get_snek(name))
        else:
            await ctx.send(embed=em)
            # await ctx.send(name)

            # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!

    @command()
    async def snake(self, ctx: Context, x=8, y=8):

        snake = []  # define snake (where snake sections are stored)
        head = [x // 2, y]  # define head (where current snake head is stored)
        apple = (random.randrange(x), random.randrange(y))  # define apple (where current apple position is stored)

        userID = ctx.author.id
        facing = 0

        snake.append(head)
        running = True

        board = "\n " + ":black_large_square:" * x + ":black_large_square::black_large_square:"
        for yAxis in range(y):
            board += "\n:black_large_square:"
            for xAxis in range(x):
                if head == [xAxis, yAxis]:
                    board += ":snake:"
                else:
                    board += ":white_large_square:"

            board += ":black_large_square:"
        board += "\n" + ":black_large_square:" * x + ":black_large_square::black_large_square:"

        Board = discord.Embed(title="Snake!", description=board)
        snakeBoard = await ctx.send(embed=Board)

        while running:
            directionChange = True
            for mess in self.inputs:
                if mess.author.id == userID:
                    self.inputs = []

                    if mess.content == "a":
                        if directionChange:
                            facing = (facing - 1) % 4
                            directionChange = False
                        await mess.delete()

                    elif mess.content == "d":
                        if directionChange:
                            facing = (facing + 1) % 4
                            directionChange = False
                        await mess.delete()

            if facing == 0:
                head[1] -= 1
            elif facing == 1:
                head[0] += 1
            elif facing == 2:
                head[1] += 1
            else:
                head[0] -= 1

            if head[0] < 0 or head[1] < 0 or head[0] > x - 1 or head[1] > y - 1:
                await ctx.send(str(ctx.author.mention) + " become a wall :cry:")
                running = False

            # check if
            for snakeTail in snake:
                if snakeTail == tuple(head):
                    await ctx.send(str(ctx.author.mention) + " ate himself :open_mouth: ")
                    running = False

            # check if an apple was eaten
            for snakeTail in snake:
                if snakeTail == apple:
                    # if so it generates a new apple
                    apple = (random.randrange(x), random.randrange(y))
                    break
            # if no apple is eaten then the else will run.
            # So when an apple is eaten the last tuple to be added to  list (snake) will not be removed
            # this effectively makes the snake one section longer.
            else:
                snake.pop(0)
            # add the current snake head to the list snake
            snake.append(tuple(head))

            # add title
            board = """"""
            # add top of board
            board += "\n " + ":black_large_square:" * (x + 2)
            for yAxis in range(y):
                # add side of board
                board += "\n:black_large_square:"
                for xAxis in range(x):
                    # add snake sections
                    for snakeTail in snake:
                        if snakeTail == (xAxis, yAxis):
                            board += ":snake:"
                            break

                    else:
                        # add apple
                        if apple == (xAxis, yAxis):
                            board += ":apple:"
                        # add background
                        else:
                            board += ":white_large_square:"

                # add side of board
                board += ":black_large_square:"
            # add bottom of board
            board += "\n" + ":black_large_square:" * (x + 2)

            # edit message then wait for next frame
            Board = discord.Embed(title="Snake!", description=board)
            await snakeBoard.edit(embed=Board)
            await asyncio.sleep(0.9)

    # get user snake inputs
    async def on_message(self, message):
        if message.content in ("a", "d"):
            self.inputs.append(message)


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
