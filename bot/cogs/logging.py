# coding=utf-8
import logging

from aiohttp import ClientSession

from bs4 import BeautifulSoup

from discord.ext.commands import AutoShardedBot

log = logging.getLogger(__name__)


class Logging:
    """
    Debug logging module
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def on_ready(self):
        log.info('Signed in as:')
        log.info('--------------')
        log.info(f'Username: {self.bot.user.name}')
        log.info(f'User ID: {self.bot.user.id}')
        log.info('--------------')
        log.info('Serving Team 17 in Code Jam 1!')
        log.info('--------------')
        log.info("Bot connected!")
        async with ClientSession(loop=self.bot.loop) as session:
            self.bot.session = session
            self.bot.info_url = 'https://snake-facts.weebly.com/snake_names.html'
        log.info('Session created!')
        async with self.bot.session.get(self.bot.info_url).text as resp:
            self.bot.soup = BeautifulSoup(resp, 'lxml')
        log.info('Response successful!')


def setup(bot):
    bot.add_cog(Logging(bot))
    log.info("Cog loaded: Logging")
