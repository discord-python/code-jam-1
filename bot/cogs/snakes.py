# coding=utf-8
import logging
import json
from aiohttp import ClientSession
from random import choice
from time import time
from typing import Any, Dict

from discord import Embed, Color
from discord.ext.commands import AutoShardedBot, Context, command

from bot.snakegame import SnakeGame

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot
        self.game = SnakeGame((5, 5))
        self.debug = True
        # changed this to (User.id: int) in order to make it easier down the line to call. >(PC)
        self.mods = [255254195505070081, 98694745760481280]
        self.last_movement = time()
        self.movement_command = {"left": 0, "right": 0, "up": 0, "down": 0}
        self.wait_time = 2

    # docstring for get_snek needs to be cleaned up >(PC)
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

        url = f'https://en.wikipedia.org/w/api.php?action=query&titles={name}' \
              f'&prop=extracts&exlimit=1&explaintext&format=json&formatversion=2'

        # account for snakes without a page somewhere. >(PC)
        async with ClientSession() as session:
            async with session.get(url) as response:
                resp = json.loads(str(await response.read(), 'utf-8'))
                return resp

    # docstring for get needs to be cleaned up. >(PC)
    @command()
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        # Everything with snek_list should be cached >(PC)
        # SELF.BOT.SNEK_LIST OMG OMG OMG >(PC)
        # Since, on restart, the bot will forget this, it will be re-cached every time. Problem Solved in theory. >(PC)
        possible_names = 'https://en.wikipedia.org/w/api.php?action=query&titles=List_of_snakes_by_common_name' \
                         '&prop=extracts&exlimit=1&explaintext&format=json&formatversion=2'

        async with ClientSession() as session:
            async with session.get(possible_names) as all_sneks:
                resp = str(await all_sneks.read(), 'utf-8')

        # can we find a better way to do this? Doesn't seem too reliable, even though MW won't change their api. >(PC)
        snek_list = resp[409:].lower().split('\\n')

        # if name is None, choose a random snake. Need to clean up snek_list. >(PC)
        if name is None:
            name = choice(snek_list)

        # stops the command if the snek is not on the list >(PC)
        elif name.lower() not in snek_list:
            await ctx.send('This is not a valid snake. Please request one that exists.\n'
                           'You can find a list of existing snakes here: ')
            return

        # accounting for the spaces in the names of some snakes. Allows for parsing of spaced names. >(PC)
        if name.split(' '):
            name = '%20'.join(name.split(' '))

        # leaving off here for the evening. Building the embed is easy. Pulling the information is hard. /s >(PC)
        # snek_dict = await self.get_snek(name)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!
    @command()
    async def play(self, ctx: Context, order):
        """
        DiscordPlaysSnek

        Move the snek around the field and collect food.

        Valid use: `bot.play {direction}`

        With 'left', 'right', 'up' and 'down' as valid directions.
        """

        # Maybe one game at a given time, and maybe editing the original message instead of constantly posting
        # new ones? Maybe we could also ask nicely for DMs to be allowed for this if they aren't. >(PC)
        if order in self.movement_command.keys():
            self.movement_command[order] += 1

            # check if it's time to move the snek
            if time() - self.last_movement > self.wait_time:
                direction = max(self.movement_command,
                                key=self.movement_command.get)
                percentage = 100*self.movement_command[direction]/sum(self.movement_command.values())
                move_status = self.game.move(direction)

                # end game
                if move_status == "lost":
                    await ctx.send("We made the snek cry! :snake: :cry:")

                # prepare snek message
                snekembed = Embed(color=Color.red())
                snekembed.add_field(name="Score", value=self.game.score)
                snekembed.add_field(name="Winner movement",
                                    value="{dir}: {per:.2f}%".format(dir=direction, per=percentage))

                snek_head = next(emoji for emoji in ctx.guild.emojis if emoji.name == 'python')

                game_string = str(self.game).replace(":python:", str(snek_head))
                snekembed.add_field(name="Board", value=game_string, inline=False)
                if self.debug:
                    snekembed.add_field(
                        name="Debug", value="Debug - move_status: " + move_status, inline=False)

                # prepare next movement
                self.last_movement = time()
                self.movement_command = {"left": 0,
                                         "right": 0, "up": 0, "down": 0}
                await ctx.send(embed=snekembed)


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
