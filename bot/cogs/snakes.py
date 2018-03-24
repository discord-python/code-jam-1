# coding=utf-8
import asyncio
import logging
import random
from string import capwords
from typing import Any, Dict

import aiohttp

import async_timeout

from discord import Embed, Member, Reaction
from discord.ext.commands import AutoShardedBot, Context, command


log = logging.getLogger(__name__)

PYTHON_QUOTE = 'bot/cogs/data/quote.txt'
PYTHON_PIC = "http://www.pngall.com/wp-content/uploads/2016/05/Python-Logo-Free-PNG-Image.png"
DEFAULT_SNAKE = "https://pbs.twimg.com/profile_images/662615956670144512/dqsVK6Nw_400x400.jpg"

# Pegs
FIRST_EMOJI = "\U0001F489"
SECOND_EMOJI = "\U0001F48A"
THIRD_EMOJI = "\u231B"
FOURTH_EMOJI = "\u2620"
FIFTH_EMOJI = "\u2697"

EMPTY = u'\u200b'

# Results
TICK_EMOJI = "\u2714"  # Correct Peg, Correct Hole
CROSS_EMOJI = "\u274C"  # Wrong
BLANK_EMOJI = "\u26AA"  # Correct Peg Wrong Hole

# Holes
HOLE_EMOJI = "\u2B1C"

ANTIDOTE_EMOJI = [FIRST_EMOJI, SECOND_EMOJI, THIRD_EMOJI, FOURTH_EMOJI, FIFTH_EMOJI]


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        self.snake_cache = []

        # This caches the very expensive snake list operation on load
        self.setup = bot.loop.create_task(self.cache_snake_list())

    async def cache_snake_list(self):
        """
        Calls get_snake_list, which is *very* hungry, and caches it
        :return:
        """
        self.snake_cache = await self.get_snake_list()
        return

    async def get_wiki_json(self, params):
        """
        Makes a call to the Wikipedia API using the passed params and returns it as json
        :param params: Pass the params as some kind of dictionary / json thing
        :return:
        """
        async with aiohttp.ClientSession(headers={'User-Agent': 'DevBot v.10'}) as cs:
            async with async_timeout.timeout(20):
                async with cs.get("https://en.wikipedia.org/w/api.php", params=params) as r:
                    log.info(f"{r.url}: {r.status}: {r.reason}")
                    return await r.json()

    async def cont_query(self, params):
        """
        This function checks for continue within the results of the API call and then appends the params
        to continue the API call across multiple pages
        :param params: Pass the params as some kind of dictionary / json thing
        :return:
        """
        last_continue = {}

        while True:
            req = params.copy()
            req.update(last_continue)
            request = await self.get_wiki_json(req)

            if 'query' not in request:
                break

            pages = request['query']['pages']['13205433']['links']
            yield pages

            if 'continue' not in request:
                break

            last_continue = request['continue']

    async def get_snake_list(self):
        """
        This queries the API for a specific list (of snakes by common name) and returns
        a sanitized list of snake names, minus the ambiguous terms... Plus some junk ;)
        :return:
        """
        ambiguous = ["(disambiguation)", "wikipedia:", "help:", "category:", "list of"]

        snake_list = []
        result = self.cont_query(
            {'action': 'query', 'titles': 'list_of_snakes_by_common_name', 'prop': 'links', 'format': 'json'})

        async for params in result:
            listed = params
            for item in listed:
                if not any(s in item['title'].lower() for s in ambiguous):
                    snake_list.append(item['title'].lower())

        snake_list.append("trouser snake")
        snake_list = sorted(list(set(snake_list)))
        return snake_list

    async def get_snek(self, name: str = None) -> Dict[str, Any]:
        """
        On user input it validates vs the snake cache and also that the page exists
        If the page doesn't exist it sends a ssssassy message
        If the page does exist it passes off the params to get_wiki_json
        :param name: Just some sort of user input, preferably a snake.
        :return:
        """
        await self.setup  # Pauses here until the "setup" task has completed
        snake_name = name
        name = name.replace(" ", "_")  # Sanitize name for use with the API

        text_params = {'action': 'query',
                       'titles': name,
                       'prop': 'extracts',
                       'exsentences': '2',
                       'explaintext': '1',
                       'autosuggest': '1',
                       'redirects': '1',
                       'format': 'json'}

        image_name_params = {'action': 'query',
                             'titles': name,
                             'prop': 'images',
                             'redirects': '1',
                             'autosuggest': '1',
                             'imlimit': '1',
                             'format': 'json'}

        text_json = await self.get_wiki_json(text_params)
        image_name_json = await self.get_wiki_json(image_name_params)
        snake_image = DEFAULT_SNAKE

        # Here we check if *ANY* of the values a user has submitted
        # match *ANY* of the values in snake_cache

        page_id = list(text_json['query']['pages'].keys())[0]
        if page_id == "-1" or snake_name.lower() not in self.snake_cache:
            matched_snakes = []

            for snake in self.snake_cache:
                if any(s in snake for s in snake_name.lower().split()):
                    matched_snakes.append(snake)

            if matched_snakes:
                if len(matched_snakes) > 1:
                    random.shuffle(matched_snakes)
                    trimmed_snakes = []
                    for snake in matched_snakes[0:9]:
                        trimmed_snakes.append(capwords(f'{snake}') + '\n')

                    trimmed_snakes = sorted(trimmed_snakes)
                    print(f"Trimmed: {trimmed_snakes}")

                    snake_dict = {"name": "No snake found, here are some suggestions:",
                                  "snake_text": ''.join(trimmed_snakes),
                                  "snake_image": snake_image}
                    return snake_dict
                else:
                    snake = matched_snakes[0]
                    print(snake)
                    snake_dict = {"name": snake_name,
                                  "snake_text": '',
                                  "snake_image": snake_image}
                    # return await self.get_snek(snake)


            snake_dict = {"name": snake_name,
                          "snake_text": "You call that a snake?\n"
                                        "THIS is a snake!",
                          "snake_image": snake_image}
            return snake_dict

        image_id = image_name_json['query']['pages'][page_id]['images'][0]['title']

        image_url_params = {'action': 'query',
                            'titles': image_id,
                            'prop': 'imageinfo',
                            'redirects': '1',
                            'autosuggest': '1',
                            'iiprop': 'url',
                            'format': 'json'}

        image_url_json = await self.get_wiki_json(image_url_params)

        snake_image_id = list(image_url_json['query']['pages'].keys())[0]
        snake_image = image_url_json['query']['pages'][snake_image_id]['imageinfo'][0]['url']
        snake_text = text_json['query']['pages'][page_id]['extract']

        snake_dict = {"name": snake_name, "snake_text": snake_text, "snake_image": snake_image}
        return snake_dict

    @command()
    async def get(self, ctx: Context, name: str = None):
        """
        Calls get_snek and puts results inside an embed for sending
        If it matches some special checks, alternative action is taken
        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        if name is None:
            name = random.choice(self.snake_cache)
        elif name == "snakes on a plane":
            await ctx.send("https://media.giphy.com/media/5xtDartXnQbcW5CfM64/giphy.gif")
            return
        elif name == "python":
            with open(PYTHON_QUOTE, 'r') as file:
                text = file.read()
                snake_embed = Embed(color=ctx.me.color, title="SNEK")
                snake_embed.add_field(name="Python", value=f"*{text}*")
                snake_embed.set_thumbnail(url=PYTHON_PIC)
                await ctx.send(embed=snake_embed)
                return

        snake = await self.get_snek(name)
        snake_embed = Embed(color=ctx.me.color, title="SNEK")
        snake_embed.add_field(name=snake['name'], value=snake['snake_text'])
        snake_embed.set_thumbnail(url=snake['snake_image'])
        await ctx.send(embed=snake_embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!
    @command(name="bb")
    async def build_board(self, ctx: Context):
        antidote_embed = Embed(color=ctx.me.color, title="Antidote")
        antidote_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        # Generate answer
        antidote_answer = list(ANTIDOTE_EMOJI)  # duplicate list, not reference it
        random.shuffle(antidote_answer)
        log.info(antidote_answer)
        # begin board building
        board = []
        for i in range(0, 10):
            board.append(f"`{10-i:02d}` "
                         f"{HOLE_EMOJI} {HOLE_EMOJI} {HOLE_EMOJI} {HOLE_EMOJI} - "
                         f"{CROSS_EMOJI} {CROSS_EMOJI} {CROSS_EMOJI} {CROSS_EMOJI}")
            board.append(EMPTY)

        antidote_embed.add_field(name="10 guesses remaining", value="\n".join(board))
        # Display board
        board_id = await ctx.send(embed=antidote_embed)
        # add our reactions
        for emoji in ANTIDOTE_EMOJI:
            await board_id.add_reaction(emoji)

        def event_check(reaction_: Reaction, user_: Member):
            """
            Make sure that this reaction is what we want to operate on
            """

            no_restrictions = (
                # Pagination is not restricted
                user_.id == ctx.author.id
            )

            return (
                # Conditions for a successful pagination:
                all((
                    # Reaction is on this message
                    reaction_.message.id == board_id.id,
                    # Reaction is one of the pagination emotes
                    reaction_.emoji in ANTIDOTE_EMOJI,
                    # Reaction was not made by the Bot
                    user_.id != self.bot.user.id,
                    # There were no restrictions
                    no_restrictions
                ))
            )

        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=300, check=event_check)
                log.trace(f"Got reaction: {reaction}")
            except asyncio.TimeoutError:
                log.debug("Timed out waiting for a reaction")
                break  # We're done, no reactions for the last 5 minutes

        log.debug("Ending pagination and removing all reactions...")
        await board_id.clear_reactions()


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
