# coding=utf-8
import logging
from typing import Any, Dict

from discord import Embed
from discord.ext.commands import AutoShardedBot, Context, command

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

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
        return name

    async def get_danger(self, level: str = None) -> str:
        """
        Returns the human-readable version of the danger level.
        :param level: The danger level of a snek
        :return: A string that is the human readable version of passed level.
        """
        return {
            '???': 'Danger unknown',
            '---': 'Nonvenomous',
            '??🐍': 'Constrictor, danger unknown',
            '🐍': 'Constrictor, considered harmless',
            '🐍🐍': 'Constrictor, harmful',
            '🐍🐍🐍': 'Constrictor, dangerous',
            '🐍🐍🐍🐍': 'Constrictor, very dangerous',
            '🐍🐍🐍🐍🐍': 'Constrictor, extremely damgerous',
            '??💀': 'Venomous, danger unknown',
            '💀': 'Venomous, considered harmless',
            '💀💀': 'Venomous, harmful',
            '💀💀💀': 'Venomous, dangerous',
            '💀💀💀💀': 'Venomous, very dangerous',
            '💀💀💀💀💀': 'Venomous, extremely dangerous.'
        }.get(level, 'Unknown')

    @command()
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """

        snek = await self.get_snek(name)

        embed = Embed(title=snek.get('common name'), description=snek.get('description'))
        # Commented out until I know what information I have to use.
        # embed.add_field(name="More Information", value="```Species | P. regius\rGenus   | Python\rFamily  | Pythonidae```", inline=True)
        embed.add_field(snek.get('level'), value=await self.get_danger(snek.get('level')), inline=True)
        embed.set_image(url=snek.get('image'))
        embed.set_footer(text="Information from Wikipedia")
        await ctx.send(embed=embed)

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
