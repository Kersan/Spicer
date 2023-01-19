import logging
from typing import Union

import wavelink
from discord.ext import commands


class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.create_nodes())

    async def create_nodes(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, **self.bot.config.lavalink)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        logging.info(f"Node: <{node.identifier}> is ready!")

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        """Play a song with the given search query.

        If not connected, connect to our voice channel.
        """
        if ctx.author.voice is None:
            return await ctx.send("Not in voice channel")
        vc: wavelink.Player = (
            ctx.voice_client
            or await ctx.author.voice.channel.connect(cls=wavelink.Player)
        )
        if vc.queue.is_empty and not vc.is_playing():
            await vc.play(search)
        else:
            await vc.queue.put_wait(search)
            await ctx.send(f"Added `{search.title}` to the queue...", delete_after=10)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        """Skip the current song."""
        if not ctx.voice_client:
            return await ctx.send("Not playing rn!")

        if not ctx.author.voice:
            return await ctx.send("You not in vc!")

        if ctx.author.voice.channel != ctx.voice_client.channel:
            return await ctx.send("You not in my vc!")

        vc: wavelink.Player = (
            ctx.voice_client
            or await ctx.author.voice.channel.connect(cls=wavelink.Player)
        )

        await vc.stop()


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
