import io
import math
import os
from typing import List, Dict

import aiohttp
import discord
from PIL import Image

BOARD_TILE_SIZE = 56  # pixels
BOARD_PLAYER_SIZE = 20


class SnakeAndLaddersGame:
    def __init__(self, snakes, channel: discord.TextChannel, author: discord.Member):
        self.snakes = snakes
        self.channel = channel
        self.state = 'booting'
        self.author = author
        self.players: List[discord.Member] = []
        self.player_tiles: Dict[int, int] = {}
        self.avatar_images: Dict[int, Image] = {}

    async def open_game(self):
        await self._add_player(self.author)
        await self.channel.send(
            '**Snakes and Ladders**: A new game is about to start!\nMention me and type **sal.join** to participate.',
            file=discord.File(os.path.join('res', 'ladders', 'banner.jpg'), filename='Snakes and Ladders.jpg'))
        self.state = 'waiting'

    async def _add_player(self, user: discord.Member):
        self.players.append(user)
        self.player_tiles[user.id] = 1
        avatar_url = user.avatar_url_as(format='jpeg', size=32)
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as res:
                avatar_bytes = await res.read()
                im = Image.open(io.BytesIO(avatar_bytes)).resize((20, 20))
                self.avatar_images[user.id] = im

    async def player_join(self, user: discord.Member):
        for p in self.players:
            if user == p:
                await self.channel.send(user.mention + " You are already in the game.")
                return
        if self.state != 'waiting':
            await self.channel.send(user.mention + " You cannot join at this time.")
            return
        if len(self.players) is 4:
            await self.channel.send(user.mention + " The game is full!")
            return

        await self._add_player(user)

        await self.channel.send(
            "**Snake and Ladders**: " + user.mention + " has joined the game.\nThere are now " + str(
                len(self.players)) + " players in the game.")
        pass

    async def player_leave(self, user: discord.Member):
        if user == self.author:
            await self.channel.send(user.mention + " You are the author, and cannot leave the game. Execute "
                                                   "`sal.cancel` to cancel the game.")
            return
        for p in self.players:
            if user == p:
                self.players.remove(p)
                del self.player_tiles[p.id]
                await self.channel.send(user.mention + " You left the game.")
                return
        await self.channel.send(user.mention + " You are not in the match.")

    async def cancel_game(self, user: discord.Member):
        if not user == self.author:
            await self.channel.send(user.mention + " Only the author of the game can cancel it.")
            return
        await self.channel.send("**Snakes and Ladders**: Game has been canceled.")
        del self.snakes.active_sal[self.channel]

    async def start_game(self, user: discord.Member):
        if not user == self.author:
            await self.channel.send(user.mention + " Only the author of the game can start it.")
            return
        # todo: minimum players = 2, max players = 4
        if not self.state == 'waiting':
            await self.channel.send(user.mention + " The game cannot be started at this time.")
            return
        self.state = 'starting'
        player_list = ', '.join(user.mention for user in self.players)
        await self.channel.send("**Snake and Ladders**: The game is starting!\nPlayers: " + player_list)
        await self.start_round()
        return

    async def start_round(self):
        board_img = Image.open(os.path.join('res', 'ladders', 'board.jpg'))
        for i, player in enumerate(self.players):
            tile = self.player_tiles[player.id]
            tile_coordinates = self._board_coordinate_from_index(tile)
            x_offset = 8 + tile_coordinates[0] * BOARD_TILE_SIZE
            y_offset = (10 * BOARD_TILE_SIZE) - (9 - tile_coordinates[1]) * BOARD_TILE_SIZE - BOARD_PLAYER_SIZE
            if i % 2 != 0:
                x_offset += BOARD_PLAYER_SIZE
            if i > 1:
                y_offset -= BOARD_PLAYER_SIZE
            board_img.paste(self.avatar_images[player.id],
                            box=(x_offset, y_offset))
        stream = io.BytesIO()
        board_img.save(stream, format='JPEG')
        board_file = discord.File(stream.getvalue(), filename='Board.jpg')
        await self.channel.send("**Snakes and Ladders**: A new round has started! Current board:", file=board_file)
        player_list = '\n'.join((user.mention + ": Tile " + str(self.player_tiles[user.id])) for user in self.players)
        await self.channel.send(
            "**Current positions**:\n" + player_list + "\n\nMention me with **roll** to roll the dice!")

    def _board_coordinate_from_index(self, index: int):
        # converts the tile number to the x/y coordinates for graphical purposes
        y_level = 9 - math.floor((index - 1) / 10)
        is_reversed = math.floor((index - 1) / 10) % 2 != 0
        x_level = (index - 1) % 10
        if is_reversed:
            x_level = 9 - x_level
        return x_level, y_level
