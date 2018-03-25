# coding=utf-8
import logging
from difflib import get_close_matches
from enum import Enum
from random import choice
from typing import Any, Dict, Tuple

from aiohttp import ClientSession
from bs4 import BeautifulSoup

import discord
from discord.ext.commands import AutoShardedBot, Context, command

from bot.constants import EMOJI_SERVER
from bot.selectors import (
    DID_YOU_KNOW_SELECTOR,
    SCIENTIFIC_NAME_SELECTOR,
    SNEK_MAP_SELECTOR
)

log = logging.getLogger(__name__)


TICTACTOE_REACTIONS = {
    (0, 0): '↖',
    (0, 1): '⬆',
    (0, 2): '↗',
    (1, 0): '⬅',
    (1, 1): '☀',
    (1, 2): '➡',
    (2, 0): '↙',
    (2, 1): '⬇',
    (2, 2): '↘'
}


class TicTacToeSymbol(Enum):

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        self.game_emojis = {}
        for e in bot.get_guild(EMOJI_SERVER):
            self.game_emojis[e.name] = e.id

        self.NOT_SET = '⬜'
        self.USER_FIELD = '🐍'
        self.BOT_FIELD = str(bot.get_emoji(self.game_emojis.get('Python')))


class TicTacToePlayer(Enum):
    BOT = 1
    USER = 2


class TicTacToeBoard:
    def __init__(self, ctx: Context):
        self.board = [
            '⬜⬜⬜',
            '⬜⬜⬜',
            '⬜⬜⬜'
        ]
        self.ctx = ctx
        self.msg = None
        self.player = ctx.author
        self.turn_user = choice(tuple(TicTacToePlayer))
        self.winner = None

    def __str__(self):
        return '\n'.join(self.board)

    def advance_turn(self):
        """Switches the active player."""

        if self.turn_user == TicTacToePlayer.BOT:
            self.turn_user = TicTacToePlayer.USER
        else:
            self.turn_user = TicTacToePlayer.BOT

    def can_set(self, coordinates: Tuple[int, int]):
        """Checks if the given coordinate pair can be set."""

        field = self.board[coordinates[0]][coordinates[1]]
        return field == TicTacToeSymbol.NOT_SET

    def get_random_open_field(self) -> Tuple[int, int]:
        """Returns a random open field for the bot to mark."""

        return choice([
            choice([
                field for field in line if field == TicTacToeSymbol.NOT_SET
            ]) for line in self.board if any(
                field == TicTacToeSymbol.NOT_SET for field in line
            )
        ])

    def is_valid_reaction(self, user, msg_reaction):
        """
        A check for `ctx.wait_for` to ensure
        that an entered reaction was valid.
        """

        message_valid = msg_reaction.message == self.ctx.message
        user_valid = user == self.player
        for coordinates, reaction in TICTACTOE_REACTIONS.items():
            if msg_reaction == reaction and self.can_set(coordinates):
                return message_valid and user_valid
        return False

    def mark_field(self, coordinates: Tuple[int, int]):
        """Marks the given coordinates with the current user's symbol."""

        if self.turn_user == TicTacToePlayer.BOT:
            symbol = TicTacToeSymbol.BOT_FIELD
        else:
            symbol = TicTacToeSymbol.USER_FIELD

        self.board[coordinates[0]][coordinates[1]] = symbol

    async def send(self):
        """Sends the board to the context passed to the constructor."""

        self.msg = await self.ctx.send(str(self))
        for reaction in TICTACTOE_REACTIONS.values():
            await self.msg.add_reaction(reaction)

    async def update_message(self):
        """
        Edits the original board sent through
        `send` to display an updated board.
        Blindly assumes that `send` was called previously.
        """

        await self.msg.edit(content=str(self))


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def on_ready(self):
        self.session = ClientSession(loop=self.bot.loop)
        self.info_url = 'https://snake-facts.weebly.com/'
        log.info('Session created.')

        with open('./snakes.txt', encoding='utf-8') as f:
            self.sneks = f.read().split('\n')
            for i, snek in enumerate(self.sneks):
                self.sneks[i] = snek.replace('\u200b', '').replace('\ufeff', '')
        log.info('Snakes loaded.')

    def no_sneks_found(self, name):
        '''Helper function if the snake was not found in the directory.'''
        em = discord.Embed(
            title='No snake found.',
            color=discord.Color.green()
        )

        snakes = get_close_matches(name, self.sneks)

        if snakes:
            em.description = 'Did you mean...\n'
            em.description += '\n'.join(f'`{x}`' for x in snakes)
        else:
            snakes = 'https://github.com/SharpBit/code-jam-1/blob/master/snakes.txt'
            em.description = f'No close matches found. Click [here]({snakes}) for the list of available snakes.'

        return em

    def format_info(self, data):
        '''Formats the info with the given data.'''
        em = discord.Embed(
            title=f"{data['name']} ({data['scientific-name']})",
            description=data['description'],
            color=discord.Color.green(),
            url=data['url']
        )

        em.set_image(url=data['image-url'])
        em.set_thumbnail(url=data['map-url'])

        return em

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
        if name:
            if name not in self.sneks:
                return self.no_sneks_found(name)
        else:
            name = choice(self.sneks)

        snake = name.lower().replace(' ', '-').replace("'", '')
        url = f'{self.info_url}{snake}.html'

        async with self.session.get(url) as resp:
            info = await resp.read()
            soup = BeautifulSoup(info, 'lxml')

        img = soup.find(attrs={'property': {'og:image'}})['content']
        names = soup.find('td', class_='wsite-multicol-col')
        sci_name = soup.select(SCIENTIFIC_NAME_SELECTOR)[0].text.strip()
        location_map = soup.select(SNEK_MAP_SELECTOR)[0]['src']
        description_tag = soup.find(attrs={'property': {'og:description'}})

        info = {
            'name': names.h1.string,
            'scientific-name': sci_name,
            'image-url': img,
            'map-url': f'{self.info_url}{location_map[1:]}',
            'description': description_tag['content'],
            'url': url
        }

        return info

    async def get_snek_fact(self):
        '''Helper function to get a snake fact.'''
        page = choice(self.sneks).replace(' ', '-').replace("'", '')
        url = f'{self.info_url}{page}.html'

        async with self.session.get(url) as resp:
            response = await resp.read()
            soup = BeautifulSoup(response, 'lxml')
            fact = soup.select(DID_YOU_KNOW_SELECTOR)[0].text

        em = discord.Embed(
            title='Did you know?',
            description=fact[13:],
            color=discord.Color.green()
        )

        return em

    @command(aliases=['snakes.get', 'snakes.get()', 'get()'])
    async def get(self, ctx: Context, *, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        # Sends info about the programming language
        if name:
            if name.lower() == 'python':
                # Python language info.
                em = discord.Embed(
                    title='Python (Pseudo anguis)',
                    description='Python is an interpreted high-level programming language for general-purpose programming. '
                                'Created by Guido van Rossum and first released in 1991, '
                                'Python has a design philosophy that emphasizes code readability, '
                                'notably using significant whitespace.',
                    color=discord.Color.blurple()
                )

                em.set_thumbnail(url='https://ih0.redbubble.net/image.80621508.8934/flat,800x800,075,t.u1.jpg')
                em.set_image(url='https://www.python.org/static/community_logos/python-logo-master-v3-TM.png')
                return await ctx.send(embed=em)
        data = await self.get_snek(name)
        # if the snake is not found
        if isinstance(data, discord.Embed):
            return await ctx.send(embed=data)
        # format the given data
        em = self.format_info(data)
        await ctx.send(embed=em)

    @command(aliases=['getsnekfact', 'snekfact()', 'get_snek_fact()'])
    async def snekfact(self, ctx: Context):
        '''
        Gets a randomsnek fact from the "Did you know?" cards
        that the website has on the right hand side.
        '''
        await ctx.send(embed=await self.get_snek_fact())

    @command()
    async def tictactoe(self, ctx: Context):
        """
        Starts a game of Tic Tac Toe with the author.
        Only one instance of the game per player is allowed at a time.
        """

        game = TicTacToeBoard(ctx)
        await game.send()
        while game.winner is None:
            if game.turn_user == TicTacToePlayer.BOT:
                field = game.get_random_open_field()
                game.mark_field(field)
            else:
                _, direction = await self.bot.wait_for(
                    'reaction', check=game.is_valid_reaction
                )
                game.mark_field(
                    next(
                        coords for coords in TICTACTOE_REACTIONS
                        if TICTACTOE_REACTIONS[coords] == direction
                    )
                )

            game.advance_turn()
            await game.update_message()


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
