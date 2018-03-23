# coding=utf-8
import logging
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
        self.mods = ["kr4n3x#5014", "(PC) Refisio#9732"]
        self.last_movement = time()
        self.movement_command = {"left": 0, "right": 0, "up": 0, "down": 0}
        self.wait_time = 2

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

    @command()
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!
    @command()
    async def play(self, ctx: Context, order):
        """
        DiscordPlaysSnek

        Move the snek around the field and collect food.

        Valid use: `bot.play {direction}`

        With 'left', 'right', 'up' and 'down' as valid directions.
        """

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
