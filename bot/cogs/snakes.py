# coding=utf-8
import json
import logging
import os
import random
import urllib
from typing import Any, Dict

import aiohttp

import discord
from discord.ext.commands import AutoShardedBot, Context, command

from titlecase import titlecase

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def get_snek_qwant_json(self, snake_name: str) -> str:
        """
        Gets the json from Unsplash for a given snake query
        :param snake_name: name of the snake
        :return: the full JSON from the search API
        """
        head = {
            'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/45.0.2454.101 Safari/537.36'),
        }
        url = f'https://api.qwant.com/api/search/images?count=5&offset=1&q={urllib.parse.quote(snake_name)}+snake'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=head) as response:
                response = await response.read()
                return json.loads(response.decode("utf-8"))

    async def get_snek_image(self, name: str) -> str:
        """
        Gets the URL of a snake image
        :param name: name of snake
        :return: image url
        """
        json_response = await self.get_snek_qwant_json(name)
        result_count = len(json_response["data"]["result"]["items"])
        if 3 > result_count > 1:
            rand = random.randint(0, result_count - 1)
        if result_count == 1:
            rand = 0
        else:
            rand = random.randint(0, 3)  # prevents returning the same image every time
        try:
            choice = str(json_response["data"]["result"]["items"][rand]["media"])
        except IndexError:
            # if no(t enough) images are returned...
            return 'https://dksignmt.com/wp-content/uploads/2015/01/404-Im%C3%A1gen-14.png'   # 404 image
        return choice

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
        base_url = "https://protected-reef-75100.herokuapp.com/"
        random_url = 'https://protected-reef-75100.herokuapp.com/random_snake'
        search_url = base_url + 'search'
        token = os.getenv('ACCESS_TOKEN')
        headers = {'Authorization': f'Token {token}'}
        snake_info = {}
        if not name:
            # get a random snake...
            async with aiohttp.ClientSession() as session:
                async with session.get(random_url, headers=headers) as response:
                    response = await response.read()
                    snake_info = json.loads(response.decode("utf-8"))
                    snake_info['matches_count'] = 1
        else:
            params = {'snake': name}
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, params=params) as response:
                    # search snake endpoint something...
                    response = await response.read()
                    data = json.loads(response.decode("utf-8"))
                    try:
                        rand = random.randint(0, len(data) - 1)
                    except ValueError:
                        # handle the scenario with an empty range of (0,0)
                        rand = 0
                    try:
                        snake_info = data[rand]
                    except IndexError:
                        # handles if there is no match in the database
                        snake_info['pass'] = False
                        return snake_info
                    snake_info['matches_count'] = len(data)

        snake_info['image_url'] = await self.get_snek_image(snake_info['common_name'])
        snake_info['pass'] = True  # successful data retrieval
        return snake_info

    @command(aliases=["g"])
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        embed = discord.Embed(color=0x3E885B)
        if name and name.lower() == "python":
            # handle Python special case
            embed.add_field(
                name="Python (programming language)",
                value=(
                    "*Guido van Rossum*\n\n"
                    "This language is neither dangerous nor venomous and can be found in software globally"
                ),
                inline=False
            )
            embed.set_image(url=await self.get_snek_image("python programming language"))
        else:
            snek_info = await self.get_snek(name)
            if not snek_info['pass']:
                embed = discord.Embed(color=0xDD3D5A)
                embed.add_field(
                    name="We Couldn't Find That :snake:",
                    value=f':x: "{name}" didn\'t match anything in our database :frowning:',
                    inline=False
                )
                await ctx.channel.send(embed=embed)
                return  # break out of rest of method
            if snek_info['is_venomous']:
                # if the snake is venomous -- use the fancy check icon
                venom_info = f":white_check_mark: venomous\n\n"
            else:
                # if the snake is not venomous -- use the fancy not allowed icon
                venom_info = f":no_entry_sign: NOT venomous\n\n"
            additional_info = ''  # required to prevent referencing before assignment
            if snek_info['matches_count'] and snek_info['matches_count'] > 1:
                additional_info = f"\n\n" \
                                  f"This search matched {snek_info['matches_count']} snakes. " \
                                  f"Try creating a more specific query for information about a particular snake. " \
                                  f"(This is a random selection from the {snek_info['matches_count']}.)"
            embed.add_field(
                name=titlecase(snek_info['common_name']),
                value=(
                    f":microscope: *{titlecase(snek_info['scientific_name'])}*\n\n"
                    f"{venom_info}"
                    f":globe_with_meridians: Found in {snek_info['locations']}"
                    f"{additional_info}"
                ),
                inline=False
            )
            embed.set_image(url=snek_info['image_url'])
        await ctx.channel.send(embed=embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!

    @command(aliases=["f"])
    async def fact(self, ctx: Context):
        """
        Gets a random fact about snakes
        :param ctx: Context object passed from discord.py
        """
        em = discord.Embed(color=0x399600)
        em.add_field(
            name="Snake Fact",
            value=self.get_snek_fact(),
            inline=False
        )
        await ctx.channel.send(
            content=ctx.message.author.mention,
            embed=em
        )

    def get_snek_fact(self) -> str:
        with open('bot/cogs/resources/facts.json', 'r', encoding="utf8") as f:
            data = json.load(f)
        choice = random.randint(0, len(data['facts']) - 1)
        return data['facts'][choice]


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
