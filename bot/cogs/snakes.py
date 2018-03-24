# coding=utf-8
import logging
from typing import Any, Dict
import json
import random

from discord.ext.commands import AutoShardedBot, Context, command
from discord import Embed

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def get_snek(self, name: str = None) -> Dict[str, Any]:
        with open('bot/db/snakes.json', 'r') as file:
                snakes_dict = json.load(file)

        if name == None or len(name) == 0:
            _, snake_info = random.choice(list(snakes_dict.items()))
        
        elif len(name) > 0:
            snake = snakes_dict[name]
            if snake['name'] != "Python":
                snake_info = {
                    'name': snake['name'],
                    'description': snake['description'],
                    'location': snake['location'],
                    'venomous': snake['venomous'],
                    'image': snake['image']
                }
            else:
                snake_info = {
                    'name': snake['name'],
                    'description': snake['description'],
                    'creator': snake['creator'],
                    'created': snake['created'],
                    'image': snake['image']
                }

        return snake_info


    @command(name='get')
    async def get(self, ctx: Context, name: str = None):
        snake_info = await self.get_snek(name)
        
        embed = Embed(
            title=snake_info['name'],
            description=snake_info['description']
        )

        if snake_info['name'] != "Python":
            embed.add_field(name="Where can you find them?",value=snake_info['location'])
            embed.add_field(name="Are they venomous?",value=snake_info['venomous'])
            embed.set_image(url=snake_info['image'])
        else:
            embed.add_field(name="Who created it?",value=snake_info['creator'])
            embed.add_field(name="When was it created?",value=snake_info['created'])
            embed.set_thumbnail(url=snake_info['image'])

        await ctx.send(embed=embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
