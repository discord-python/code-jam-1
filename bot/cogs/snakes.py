# coding=utf-8
import logging

import discord
from discord.ext.commands import AutoShardedBot, Context, command

from bot.sneks.sneks import Embeddable, SnakeDef, scrape_itis, snakify
from pymarkovchain import MarkovChain
from bot.sneks.hatching import hatching,hatching_snakes
import asyncio
import random

log = logging.getLogger(__name__)

# the python snek
SNEK_PYTHON = SnakeDef(
    common_name="Python",
    species="Pseudo lingua",
    image_url="https://momoperes.ca/files/pythonpls.png",
    family="sneks-that-byte",
    genus="\"Programming Language\"",
    short_description="python is a language that you learn because tensorflow has an API for it",
    wiki_link="https://en.wikipedia.org/wiki/Pseudocode"
)

# consolation snek :(
SNEK_SAD = discord.Embed()
SNEK_SAD.title = "sad snek :("
SNEK_SAD.set_image(url="https://momoperes.ca/files/sadsnek.jpeg")

# max messages to train on per user 
MSG_MAX = 100

class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def get_snek(self, name: str = None) -> Embeddable:
        """
        Gets information about a snek
        :param name: the name of the snek
        :return: snek
        """
        if name is not None and name.lower() == "python":
            # return info about language
            return SNEK_PYTHON

        web_search = search.search(name)
        if(web_search is not None):
            return web_search
        # todo: find a random snek online if there name is null
        # todo: scrape the web to find the lost sneks
        if name is not None:
            return await scrape_itis(name)

    @command(name="snakes.get()", aliases=["snakes.get"])
    async def get(self, ctx: Context, name: str = None):
        """
        Get info about a snek!
        :param ctx: context
        :param name: name of snek
        :return: snek
        """
        # fetch data for a snek
        await ctx.send("Fetching data for " + name + "..." if name is not None else "Finding a random snek!")
        data = await self.get_snek(name)
        if data is None:
            await ctx.send("sssorry I can't find that snek :(", embed=SNEK_SAD)
            return
        channel: discord.TextChannel = ctx.channel
        embed = data.as_embed()
        log.debug("Sending embed: " + str(data.__dict__))
        await channel.send(embed=embed)


    @command(name="snakes.snakeme()",aliases=["snakes.snakeme","snakeme"])
    async def snakeme(self, ctx: Context):
        """
        How would I talk if I were a snake? 
        :param ctx: context
        :return: you, snakified based on your Discord message history
        """
        mentions = list(filter(lambda m:m.id != self.bot.user.id,ctx.message.mentions))
        author = ctx.message.author if(len(mentions) == 0) else ctx.message.mentions[0]
        channel : discord.TextChannel = ctx.channel

        channels = [ channel for channel in ctx.message.guild.channels if isinstance(channel,discord.TextChannel) ]
        channels_messages = [ await channel.history(limit=10000).flatten() for channel in channels]
        msgs = [msg for channel_messages in channels_messages for msg in channel_messages][:MSG_MAX]

        my_msgs = list(filter(lambda msg: msg.author.id == author.id, msgs))
        my_msgs_content = "\n".join(list(map(lambda x:x.content, my_msgs)))

        mc = MarkovChain()
        mc.generateDatabase(my_msgs_content)
        sentence = mc.generateString()

        snakeme = discord.Embed()
        snakeme.set_author(name="{}#{}".format(author.name,author.discriminator), icon_url = "https://cdn.discordapp.com/avatars/{}/{}".format(author.id,author.avatar) if author.avatar is not None else "https://img00.deviantart.net/eee3/i/2017/168/3/4/discord__app__avatar_rev1_by_nodeviantarthere-dbd2tp9.png")
        snakeme.description = "*{}*".format(snakify(sentence) if sentence is not None else ":question: Not enough messages")
        await channel.send(embed=snakeme)
    

    @command(name="snakes.hatch()",aliases=["snakes.hatch","hatch"])
    async def hatch(self,ctx: Context):
        """ 
        Hatches your personal snake
        :param ctx: context
        :return: baby snake
        """
        channel: discord.TextChannel = ctx.channel

        my_snake = list(hatching_snakes.keys())[random.randint(0,3)]
        my_snake_img = hatching_snakes[my_snake]
        print(my_snake_img)

        m = await channel.send(embed=discord.Embed(description="Hatching your snake :snake:..."))
        await asyncio.sleep(1)

        for i in range(len(hatching)):
            hatch_embed = discord.Embed(description = hatching[i])
            await m.edit(embed = hatch_embed)
            await asyncio.sleep(1)
        # await m.edit(embed = discord.Embed().set_thumbnail(url="https://i.imgur.com/5QHH4If.jpg"))
        await asyncio.sleep(1)
        await m.delete()

        my_snake_embed = discord.Embed(description=":tada: Congrats!! You hatched: **{}**".format(my_snake))
        my_snake_embed.set_thumbnail(url=my_snake_img)
        my_snake_embed.set_footer(text=" Owner: {}#{}".format(ctx.message.author.name,ctx.message.author.discriminator))
        await channel.send(embed=my_snake_embed)
        

def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
