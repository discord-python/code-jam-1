# coding=utf-8
import asyncio
import logging
import random
import re
import textwrap
from typing import Any, Dict

import aiohttp
import async_timeout
import discord
from discord.ext.commands import AutoShardedBot, Context, command, bot_has_permissions

from bot.converters import Snake
from bot.decorators import locked
from bot.utils import disambiguate

log = logging.getLogger(__name__)
URL = "https://en.wikipedia.org/w/api.php?"


class Snakes:
    """
    Snake-related commands
    """

    # I really hope this works
    wiki_sects = re.compile(r'(?:=+ (.*?) =+)(.*?\n\n)', flags=re.DOTALL)
    wiki_brief = re.compile(r'(.*?)(=+ (.*?) =+)', flags=re.DOTALL)

    valid = ('gif', 'png', 'jpeg', 'jpg', 'webp')

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def fetch(self, session, url, params=None):
        if params is None:
            params = {}

        async with async_timeout.timeout(10):
            async with session.get(url, params=params) as response:
                return await response.json()

    async def get_snek(self, name: str) -> Dict[str, Any]:
        """
        Go online and fetch information about a snake

        The information includes the name of the snake, a picture of the snake, and various other pieces of info.
        What information you get for the snake is up to you. Be creative!

        If "python" is given as the snake name, you should return information about the programming language, but with
        all the information you'd provide for a real snake. Try to have some fun with this!

        :param name: The name of the snake to get information for - omit for a random snake
        :return: A dict containing information on a snake
        """
        snake_info = {}

        async with aiohttp.ClientSession() as session:
            params = {
                'format': 'json',
                'action': 'query',
                'list': 'search',
                'srsearch': name,
                'utf8': '',
                'srlimit': '1',
            }

            json = await self.fetch(session, URL, params=params)

            # wikipedia does have a error page
            try:
                pageid = json["query"]["search"][0]["pageid"]
            except KeyError:
                # Wikipedia error page ID(?)
                pageid = 41118

            params = {
                'format': 'json',
                'action': 'query',
                'prop': 'extracts|images|info',
                'exlimit': 'max',
                'explaintext': '',
                'inprop': 'url',
                'pageids': pageid
            }

            json = await self.fetch(session, URL, params=params)

            # constructing dict - handle exceptions later
            try:
                snake_info["title"] = json["query"]["pages"][f"{pageid}"]["title"]
                snake_info["extract"] = json["query"]["pages"][f"{pageid}"]["extract"]
                snake_info["images"] = json["query"]["pages"][f"{pageid}"]["images"]
                snake_info["fullurl"] = json["query"]["pages"][f"{pageid}"]["fullurl"]
                snake_info["pageid"] = json["query"]["pages"][f"{pageid}"]["pageid"]
            except KeyError:
                snake_info["error"] = True
            if snake_info["images"]:
                i_url = 'https://commons.wikimedia.org/wiki/Special:FilePath/'
                image_list = []
                map_list = []
                thumb_list = []

                # Wikipedia has arbitrary images that are not snakes
                banned = [
                    'Commons-logo.svg',
                    'Red%20Pencil%20Icon.png',
                    'distribution',
                    'The%20Death%20of%20Cleopatra%20arthur.jpg',
                    'Head%20of%20holotype',
                    'locator',
                    'Woma.png',
                    '-map.',
                    '.svg',
                    'ange.',
                    'Adder%20(PSF).png'
                ]

                for image in snake_info["images"]:
                    # images come in the format of `File:filename.extension`
                    file, sep, filename = image["title"].partition(':')
                    filename = filename.replace(" ", "%20")  # Wikipedia returns good data!

                    if not filename.startswith('Map'):
                        if any(ban in filename for ban in banned):
                            log.info("the image is banned")
                        else:
                            image_list.append(f"{i_url}{filename}")
                            thumb_list.append(f"{i_url}{filename}?width=100")
                    else:
                        map_list.append(f"{i_url}{filename}")

            snake_info["image_list"] = image_list
            snake_info["map_list"] = map_list
            snake_info["thumb_list"] = thumb_list
        return snake_info

    @command(name="snakes.get()", aliases=["snakes.get"])
    @bot_has_permissions(manage_messages=True)
    @locked()
    async def get(self, ctx: Context, name: Snake = None):
        """
        Fetches information about a snake from Wikipedia.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        if name is None:
            name = Snake.random()

        data = await self.get_snek(name)

        if data.get('error'):
            return await ctx.send('Could not fetch data from Wikipedia.')

        match = self.wiki_brief.match(data['extract'])
        embed = discord.Embed(
            title=data['title'],
            description=match.group(1) if match else None,
            url=data['fullurl'],
            colour=0x59982F
        )

        fields = self.wiki_sects.findall(data['extract'])
        excluded = ('see also', 'further reading', 'subspecies')

        for title, body in fields:
            if title.lower() in excluded:
                continue
            if not body.strip():
                continue
            # Only takes the first sentence
            title, dot, _ = title.partition('.')
            # There's probably a better way to do this
            value = textwrap.shorten(body.strip(), width=200)
            embed.add_field(name=title + dot, value=value + '\n\u200b', inline=False)

        embed.set_footer(text='Powered by Wikipedia')

        emoji = 'https://emojipedia-us.s3.amazonaws.com/thumbs/60/google/3/snake_1f40d.png'
        image = next((url for url in data['image_list'] if url.endswith(self.valid)), emoji)
        embed.set_thumbnail(url=image)

        await ctx.send(embed=embed)

    @command(hidden=True)
    async def zen(self, ctx):
        """
        >>> import this

        Long time Pythoneer Tim Peters succinctly channels the BDFL's guiding principles
        for Python's design into 20 aphorisms, only 19 of which have been written down.

        You must be connected to a voice channel in order to use this command.
        """
        channel = ctx.author.voice.channel
        if channel is None:
            return

        state = ctx.guild.voice_client
        if state is not None:
            # Already playing
            return

        voice = await channel.connect()
        source = discord.FFmpegPCMAudio('zen.mp3')
        voice.play(source, after=lambda *args: asyncio.run_coroutine_threadsafe(
            voice.disconnect(), loop=ctx.bot.loop
        ))

    @command(name="snakes.guess()", aliases=["snakes.guess", "identify"])
    @locked()
    async def guess(self, ctx):
        """
        Snake identifying game!
        """
        image = None

        while image is None:
            snakes = [Snake.random() for _ in range(5)]
            answer = random.choice(snakes)

            data = await self.get_snek(answer)

            image = next((url for url in data['image_list'] if url.endswith(self.valid)), None)

        embed = discord.Embed(
            title='Which of the following is the snake in the image?',
            colour=random.randint(1, 0xFFFFFF)
        )
        embed.set_image(url=image)

        guess = await disambiguate(ctx, snakes, timeout=60, embed=embed)

        if guess == answer:
            return await ctx.send('You guessed correctly!')
        await ctx.send(f'You guessed wrong. The correct answer was {answer}.')


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
