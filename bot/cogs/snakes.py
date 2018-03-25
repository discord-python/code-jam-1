# coding=utf-8
import json
import logging
import random
from typing import Any, Dict

from discord import Embed
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
        with open('bot/db/snakes.json', 'r') as file:
                snakes_dict = json.load(file)

        if not name:
            _, snake = random.choice(list(snakes_dict.items()))

        elif name.lower() not in snakes_dict:
            snake = "Not Found"

        else:
            snake = snakes_dict[name.lower()]
            if snake['name'] == "python":
                snake = {
                    'name': snake['name'],
                    'description': snake['description'],
                    'creator': snake['creator'],
                    'created': snake['created'],
                    'image': snake['image']
                }

        return snake

    @command(name='get')
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.
        
        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        snake = await self.get_snek(name)

        if snake != "Not Found":
            embed = Embed(
                title=snake['name'].title(),
                description=snake['description']
            )

            if snake['name'] != "python":
                embed.add_field(name="Where can you find them?", value=snake['location'])
                embed.add_field(name="Are they venomous?", value=snake['venomous'])
                embed.set_image(url=snake['image'])
            else:
                embed.add_field(name="Who created it?", value=snake['creator'])
                embed.add_field(name="When was it created?", value=snake['created'])
                embed.set_thumbnail(url=snake['image'])
        else:
            embed = Embed(
                title="Snake Not Found",
                description="The snake you entered was not found."
            )

        await ctx.send(embed=embed)

    @command(name='movies')
    async def movies(self, ctx: Context, movie_name: str = None):
        """
        Shows 5 snake movies. Warning: They are all pretty bad.
        """

        with open('bot/db/movies.json', 'r') as file:
            movies_dict = json.load(file)

        if not movie_name:
            embed = Embed(
                title="Snake Movies",
                description="A list of snake movies.",
            )

            for movie in movies_dict.values():
                embed.add_field(name=movie['title'], value=f"bot.movies('{movie['title']}')\n\n")

            embed.set_thumbnail(url="https://i.imgur.com/dB38NwN.png")

        else:
            movie_name = movie_name.lower()
            if movie_name in movies_dict:
                embed = Embed(
                    title=movies_dict[movie_name]['title'],
                    description=movies_dict[movie_name]['description']
                )

                embed.add_field(name="Director", value=movies_dict[movie_name]['director'])
                embed.add_field(name="Release Date", value=movies_dict[movie_name]['released'])
                embed.set_image(url=movies_dict[movie_name]['image'])
            else:
                embed = Embed(
                    title="Movie Not Found",
                    description="The movie you entered was not found."
                )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
