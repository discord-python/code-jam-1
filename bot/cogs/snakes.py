# coding=utf-8
import asyncio
import json
import logging
import random
from typing import Tuple

from discord import Embed, FFmpegPCMAudio
from discord.ext.commands import AutoShardedBot, Context, command
from discord.opus import is_loaded, load_opus

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        self.python_image = "https://www.python.org/static/community_logos/python-logo-master-v3-TM.png"
        self.python_info = ("The Python Programming language(Python Sermone) is a dynamically typed, interpreted "
                            "programming language. It is a member of the high level programming languges usually "
                            "found in areas like backend web development data science and AI.")
        with open("bot/db/db.json", "r") as db:
            self.db = json.load(db)

    async def get_snek(self, name: str = None) -> Tuple[str, str, str]:
        """
        Go online and fetch information about a snake

        The information includes the name of the snake, a picture of the snake, and various other pieces of info.
        What information you get for the snake is up to you. Be creative!

        If "python" is given as the snake name, you should return information about the programming language, but with
        all the information you'd provide for a real snake. Try to have some fun with this!

        :param name: Optional, the name of the snake to get information for - omit for a random snake
        :return: A dict containing information on a snake
        """
        if name:
            name = name.lower()
            if name == "python":
                return ("python", self.python_info, self.python_image)
            else:
                for key in self.db.keys():
                    if key.lower() == name:
                        return (key, self.db[key][0], self.db[key][1])
        else:
            key = random.choice(list(self.db))
            return (key, self.db[key][0], self.db[key][1])

    @command()
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        snake = await self.get_snek(name)
        if snake:
            snake_embed = Embed(title=snake[0], description=snake[1])
            snake_embed.set_image(url=snake[2])
            await ctx.send(embed=snake_embed)
        else:
            await ctx.send("I was not able to find your snake, I am sorry.")

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!
    @command()
    async def hiss(self, ctx: Context):
        """
        Hisssses in a voice channel
        """
        voice_channel = ctx.message.author.voice.channel
        if voice_channel:
            voice_client = await voice_channel.connect()
            hiss = FFmpegPCMAudio("bot/db/sound1.mp3")

            def disconnect(errors):
                disconnect_coro = voice_client.disconnect()
                asyncio.run_coroutine_threadsafe(disconnect_coro, self.bot.loop)
            voice_client.play(hiss, after=disconnect)


def setup(bot):
    if not is_loaded():
        load_opus()
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
