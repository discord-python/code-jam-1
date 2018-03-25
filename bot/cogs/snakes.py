# coding=utf-8
import asyncio
import logging
import random
from string import capwords
from typing import Any, Dict

import aiohttp

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
TICK_EMOJI = "\u2705"  # Correct peg, correct hole
CROSS_EMOJI = "\u274C"  # Wrong
BLANK_EMOJI = "\u26AA"  # Correct peg, wrong hle

# Holes
HOLE_EMOJI = "\u2B1C"

ANTIDOTE_EMOJI = [FIRST_EMOJI, SECOND_EMOJI, THIRD_EMOJI, FOURTH_EMOJI, FIFTH_EMOJI]


def to_lower(argument):
    return argument.lower()


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
        # This could be done more efficiently by combining it with get_snake_list
        # However this is will do for now
        self.snake_cache = await self.get_snake_list()
        return

    async def get_wiki_json(self, params):
        """
        Makes a call to the Wikipedia API using the passed params and returns it as json
        :param params: Pass the params as some kind of dictionary / json thing
        :return:
        """
        async with aiohttp.ClientSession(headers={'User-Agent': 'DevBot v.10'}) as cs:
            async with aiohttp.Timeout(20):
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
        Builds a Wiki API query and then checks if the result contains a page
        If the cache is hit and the page exists then it pulls info
        If the cache is hit and the page does not exist, offer suggestions
        If the cache is hit once it returns the info for that hit
        If you write something stupid it'll throw a snakey-wakey error
        :param name: Just some sort of user input, preferably a snake
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

        page_id = list(text_json['query']['pages'].keys())[0]

        # Check that page exists or that snake is in cache
        if page_id == "-1" or snake_name not in self.snake_cache:
            # Build a list of matching snakes
            matched_snakes = []

            for snake in self.snake_cache:
                if any(s in snake for s in snake_name.split()):
                    matched_snakes.append(snake)

            # On cache hit start building a sorted, trimmed, random list from hits
            if matched_snakes:
                trimmed_snakes = []
                random_matched_snakes = list(matched_snakes)
                random.shuffle(random_matched_snakes)

                for snake in random_matched_snakes[0:9]:
                    trimmed_snakes.append(capwords(f'{snake}') + '\n')

                trimmed_snakes = sorted(trimmed_snakes)

                # If page doesn't exist and snake DOES exist in cache return error and suggestions
                # E.g. "corn" wont hit any snakes directly, but exists inside more than 1 result
                if page_id == "-1" and snake_name in self.snake_cache:
                    snake_dict = {"name": f"Found {capwords(snake_name)} but no page! Suggestions:",
                                  "snake_text": ''.join(trimmed_snakes),
                                  "snake_image": snake_image}
                    return snake_dict

                # If more than 1 indirect cache hit then offer suggestions based off the hits
                if len(matched_snakes) > 1:

                    snake_dict = {"name": "No snake found, here are some suggestions:",
                                  "snake_text": ''.join(trimmed_snakes),
                                  "snake_image": snake_image}
                    return snake_dict
                # If only 1 cache hit then re-run get_snek with the full term from cache
                # A good example of this in action is "bot.get rosy"
                else:
                    snake = matched_snakes[0]
                    return await self.get_snek(snake)

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

        snake_dict = {"name": capwords(snake_name), "snake_text": snake_text, "snake_image": snake_image}
        return snake_dict

    @command()
    async def get(self, ctx: Context, name: to_lower = None):
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
    @command(name="antidote")
    async def build_board(self, ctx: Context):
        """
        Antidote - Can you create the antivenom before the patient dies?
        Rules:  You have 4 ingredients for each antidote, you only have 10 attempts
                Once you synthesize the antidote, you will be presented with 4 markers
                Tick: This means you have a CORRECT ingredient in the CORRECT position
                Circle: This means you have a CORRECT ingredient in the WRONG position
                Cross: This means you have a WRONG ingredient in the WRONG position
        Info:   The game automatically ends after 5 minutes inactivity.
                You should only use each ingredient once.
        """

        # Check to see if the bot can remove reactions
        if not ctx.channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.send("Unable to start game as I dont have manage_messages permissions")
            return

        # Initialize variables
        antidote_tries = 0
        antidote_guess_count = 0
        antidote_guess_list = []
        guess_result = []
        board = []
        page_guess_list = []
        page_result_list = []
        win = False

        antidote_embed = Embed(color=ctx.me.color, title="Antidote")
        antidote_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        # Generate answer
        antidote_answer = list(ANTIDOTE_EMOJI)  # Duplicate list, not reference it
        random.shuffle(antidote_answer)
        antidote_answer.pop()
        log.info(antidote_answer)

        # Begin initial board building
        for i in range(0, 10):
            page_guess_list.append(f"{HOLE_EMOJI} {HOLE_EMOJI} {HOLE_EMOJI} {HOLE_EMOJI}")
            page_result_list.append(f"{CROSS_EMOJI} {CROSS_EMOJI} {CROSS_EMOJI} {CROSS_EMOJI}")
            board.append(f"`{i+1:02d}` "
                         f"{page_guess_list[i]} - "
                         f"{page_result_list[i]}")
            board.append(EMPTY)
        antidote_embed.add_field(name="10 guesses remaining", value="\n".join(board))
        board_id = await ctx.send(embed=antidote_embed)  # Display board

        # Add our player reactions
        for emoji in ANTIDOTE_EMOJI:
            await board_id.add_reaction(emoji)

        def event_check(reaction_: Reaction, user_: Member):
            """
            Make sure that this reaction is what we want to operate on
            """
            return (
                # Conditions for a successful pagination:
                all((
                    reaction_.message.id == board_id.id,  # Reaction is on this message
                    reaction_.emoji in ANTIDOTE_EMOJI,  # Reaction is one of the pagination emotes
                    user_.id != self.bot.user.id,  # Reaction was not made by the Bot
                    user_.id == ctx.author.id  # There were no restrictions
                ))
            )

        # Begin main game loop
        while not win and antidote_tries < 10:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=300, check=event_check)
            except asyncio.TimeoutError:
                log.debug("Timed out waiting for a reaction")
                break  # We're done, no reactions for the last 5 minutes

            if antidote_tries < 10:
                if antidote_guess_count < 4:
                    if reaction.emoji in ANTIDOTE_EMOJI:
                        antidote_guess_list.append(reaction.emoji)
                        antidote_guess_count += 1

                    if antidote_guess_count == 4:  # Guesses complete
                        antidote_guess_count = 0
                        page_guess_list[antidote_tries] = " ".join(antidote_guess_list)
                        log.info(f"Guess: {' '.join(antidote_guess_list)}")

                        # Now check guess
                        for i in range(0, len(antidote_answer)):
                            if antidote_guess_list[i] == antidote_answer[i]:
                                guess_result.append(TICK_EMOJI)
                            elif antidote_guess_list[i] in antidote_answer:
                                guess_result.append(BLANK_EMOJI)
                            else:
                                guess_result.append(CROSS_EMOJI)
                        guess_result.sort()
                        page_result_list[antidote_tries] = " ".join(guess_result)
                        log.info(f"Guess Result: {' '.join(guess_result)}")

                        # Rebuild the board
                        board = []
                        for i in range(0, 10):
                            board.append(f"`{i+1:02d}` "
                                         f"{page_guess_list[i]} - "
                                         f"{page_result_list[i]}")
                            board.append(EMPTY)

                        # Remove Reactions
                        for emoji in antidote_guess_list:
                            await board_id.remove_reaction(emoji, user)

                        if antidote_guess_list == antidote_answer:
                            win = True

                        antidote_tries += 1
                        guess_result = []
                        antidote_guess_list = []

                        antidote_embed.clear_fields()
                        antidote_embed.add_field(name=f"{10 - antidote_tries} "
                                                      f"guesses remaining",
                                                 value="\n".join(board))
                        # Redisplay the board
                        await board_id.edit(embed=antidote_embed)

        # Winning / Ending Screen
        if win is True:
            antidote_embed = Embed(color=ctx.me.color, title="Antidote")
            antidote_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            antidote_embed.set_image(url="https://i.makeagif.com/media/7-12-2015/Cj1pts.gif")
            antidote_embed.add_field(name=EMPTY,
                                     value=f"You have created the snake antidote!\n"
                                           f"You had {10 - antidote_tries} tries remaining")
            await board_id.edit(embed=antidote_embed)
        else:
            antidote_embed = Embed(color=ctx.me.color, title="Antidote")
            antidote_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            antidote_embed.set_image(url="https://media.giphy.com/media/ceeN6U57leAhi/giphy.gif")
            antidote_embed.add_field(name=EMPTY,
                                     value=f"Sorry you didnt make the antidote in time.\n"
                                           f"The formula was {' '.join(antidote_answer)}")
            await board_id.edit(embed=antidote_embed)

        log.debug("Ending pagination and removing all reactions...")
        await board_id.clear_reactions()


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
