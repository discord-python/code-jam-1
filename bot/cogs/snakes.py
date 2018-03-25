# coding=utf-8
import logging
from typing import Any, Dict
from bot.cogs import WikiListener
from discord.ext.commands import AutoShardedBot, Context, command
import discord
import aiohttp

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def is_snek(self, name: str = None) -> Dict[str, Any]:
        if name in WikiListener.get_all_snek():
            return True
        else:
            return False

    @command()
    async def get(self, ctx: Context, name: str = None):
        if name is None:
            ctx.send("Ensure your command specifies the correct arguments.")
        state = await self.is_snek(name)
        if state:
            if WikiListener.get_snek_scientific(name) is None:
                title = await WikiListener.get_snek_scientific(name)
                description = await WikiListener.get_snek_description(name)
                embed = discord.Embed(title=f"{name}", description=f"{description}", color=0x00ff80)
                try:
                    thumbnail = await WikiListener.get_snek_thumbnail(name)
                    embed.set_thumbnail(url=f'{thumbnail}')
                except aiohttp.web.HTTPExceptionError:
                    pass
                await ctx.send(embed=embed)
            else:
                title = await WikiListener.get_snek_scientific(name)
                description = await WikiListener.get_snek_description(name)
                embed = discord.Embed(title=f"{name}", description=f"{description}", color=0x00ff80)
                embed.set_author(name=f"{title}")
                try:
                    thumbnail = await WikiListener.get_snek_thumbnail(name)
                    embed.set_thumbnail(url=f'{thumbnail}')
                except aiohttp.web.HTTPClientError:
                    pass
                await ctx.send(embed=embed)
        else:
            await ctx.channel.send(f"Did not find {name} in the database.")

    @command()
    async def quiz(self, ctx: Context, name: str = None):
        async def addmoji(msg, emojilist):
            for emoji in emojilist:
                await msg.add_reaction(emoji)

        quemoji = ['🇦', '🇧', '🇨', '🇩']
        question = ['Which snek is the sneakiest snek?', '🇦Cobra\n\n🇧Regular Snek\n\n🇨Python\n\n🇩<Cobra></Cobra>', '🇨']
        em = discord.Embed(title=question[0], description=question[1])
        channel = ctx.channel
        quiz = await channel.send('', embed=em)
        await addmoji(quiz, quemoji)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji)   

        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError as err:
            await channel.send('👎')            
        else:
            if str(reaction.emoji) == question[2]:
                await channel.send('👍')
            else:
                pass


# Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!
def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
