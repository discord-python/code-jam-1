# coding=utf-8
import logging

from discord.ext.commands import AutoShardedBot

log = logging.getLogger(__name__)


class Logging:
    """
    Debug logging module
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def on_ready(self):
        log.info("Bot connected!")


def setup(bot):
    bot.add_cog(Logging(bot))
    log.info("Cog loaded: Logging")
