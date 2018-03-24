# coding=utf-8
import logging

from aiohttp import ClientSession

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

        self.bot.session = ClientSession(loop=self.bot.loop)
        self.bot.info_url = 'https://snake-facts.weebly.com/'
        log.info('Session created!')

        with open('./snakes.txt', encoding='utf-8') as f:
            self.bot.sneks = f.read().split('\n')
            for i, snek in enumerate(self.bot.sneks):
                self.bot.sneks[i] = snek.replace('\u200b', '').replace('\ufeff', '')

        log.info('Snakes loaded.')


def setup(bot):
    bot.add_cog(Logging(bot))
    log.info("Cog loaded: Logging")
