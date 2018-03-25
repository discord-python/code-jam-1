# coding=utf-8
import asyncio
import logging
import random
from typing import Any, Dict

import aiohttp

from bs4 import BeautifulSoup

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
        # await ctx.send(BeautifulSoup(text, 'lxml').find("title"))
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
    async def snake(self, ctx: Context, x=10, y=7):
        board = """"""
        running = True
        snake = []

        head = [x // 2, y // 2]
        snake.append(head)
        userID = ctx.author.id

        facing = 0
        snake.append(head)
        apple = (random.randint(0, x), random.randint(0, y))

        board += "```\n " + "#" * x + "##"
        for yAxis in range(y):
            board += "\n #"
            for xAxis in range(x):
                if head == [xAxis, yAxis]:
                    board += "X"
                else:
                    board += "0"

            board += "#"
        board += "\n " + "#" * x + "##```"

        snakeBoard = await ctx.send(board)

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

            if tuple(head) == any(snake):
                await ctx.send(str(ctx.author.mention) + " ate yourself...")
                break
            if head[0] < 0 or head[1] < 0 or head[0] > x or head[1] > y:
                await ctx.send(str(ctx.author.mention) + " ate a wall?")
                break

            for snakeTail in snake:
                if snakeTail == apple:
                    apple = (random.randint(0, x), random.randint(0, y))
                    break
            else:
                snake.pop(0)
            snake.append(tuple(head))

            board = """Snake! {}\n""".format(ctx.author.mention)
            board += "```\n " + "#" * x + "##"
            for yAxis in range(y):
                board += "\n #"
                for xAxis in range(x):
                    for snakeTail in snake:
                        if snakeTail == (xAxis, yAxis):
                            board += "X"
                            break
                    else:
                        if apple == (xAxis, yAxis):
                            board += "@"
                        else:
                            board += "0"

                board += "#"
            board += "\n " + "#" * x + "##```"

            await snakeBoard.edit(content=board)
            await asyncio.sleep(0.9)

    async def on_message(self, message):
        if message.content in ("a", "d"):
            self.inputs.append(message)


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
