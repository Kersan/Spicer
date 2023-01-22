import asyncio
import logging
from typing import Union

import wavelink
from discord import VoiceChannel
from discord.ext import commands


async def voice_check(ctx: commands.Context):
    if not ctx.author.voice:
        await ctx.reply("You not in vc!")
        return False
    if not ctx.voice_client:
        return True
    if ctx.author.voice.channel != ctx.voice_client.channel:
        await ctx.reply("You not in my vc!")
        return False
    return True


async def get_player(ctx: commands.Context):
    """Get the player for the guild."""
    return ctx.voice_client or await ctx.author.voice.channel.connect(
        cls=wavelink.Player
    )


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

    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self, player: wavelink.Player, track: wavelink.Track, reason
    ):
        if not player.queue and not player.track:
            await asyncio.sleep(300)
            if not player.queue and not player.track:
                await player.disconnect()

        else:
            await player.play(player.queue.get())

    @commands.command(name="connect", aliases=["join"])
    async def connect_command(
        self, ctx: commands.Context, *, channel: VoiceChannel = None
    ):
        """Connect to a voice channel."""
        try:
            channel = channel or ctx.author.voice.channel
        except AttributeError:
            return await ctx.send(
                "No voice channel to connect to. Please either provide one or join one."
            )

        vc: wavelink.Player = await channel.connect(cls=wavelink.Player)
        return vc

    @commands.command(name="disconnect", aliases=["leave"])
    @commands.check(voice_check)
    async def disconnect_command(self, ctx: commands.Context):
        """Disconnect from a voice channel."""

        vc: wavelink.Player = (
            ctx.voice_client
            or await ctx.author.voice.channel.connect(cls=wavelink.Player)
        )

        if vc.queue:
            vc.queue.clear()

        await ctx.voice_client.disconnect()
        return await ctx.send("Disconnected.")

    @commands.command()
    @commands.check(voice_check)
    async def play(
        self, ctx: commands.Context, *, track: Union[wavelink.YouTubeTrack, str, None]
    ):
        """Play a song with the given search query.
        If not connected, connect to our voice channel.

        When the query is a URL, we will attempt to play the song.
        If not, we will attempt to search for a song.
        """

        final = None
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            vc = await self.connect_command(ctx, channel=ctx.author.voice.channel)

        if not track and vc.is_paused:
            await vc.resume()
            return await self.resume_command(ctx)

        if isinstance(track, wavelink.YouTubeTrack):
            final = track

        elif isinstance(track, str):
            final = await wavelink.YouTubeTrack.search(query=track, return_first=True)

        if not final:
            return await ctx.send("No match found!")

        if vc.track:
            vc.queue.put(final)
            return await ctx.send(f"Added to queue: {final.title}")

        vc.queue.put(final)
        await vc.play(vc.queue.get())
        return await ctx.send(f"Playing: {final.title}")

    @commands.command(name="queue", aliases=["q"])
    async def queue_command(self, ctx: commands.Context):
        """Show the current queue."""

        if not ctx.voice_client:
            return await ctx.send("Not playing rn!")

        vc: wavelink.Player = ctx.voice_client

        if not vc.queue:
            return await ctx.send("No songs queued!")

        queue = "\n".join(f"{i} - {t.title}" for i, t in enumerate(vc.queue, start=1))
        await ctx.send(f"```{queue}```")

    @commands.command(name="skip", aliases=["s"])
    @commands.check(voice_check)
    async def skip_command(self, ctx: commands.Context):
        """Skip the current song."""

        vc: wavelink.Player = await get_player(ctx)

        if not vc.queue:
            await vc.stop()
            return await ctx.send("No songs queued, stopping!")

        await vc.play(vc.queue.get())
        return await ctx.send(f"Skipped, now playing: {vc.track}")

    @commands.command(name="pause", aliases=["stop"])
    @commands.check(voice_check)
    async def pause_command(self, ctx: commands.Context):
        """Pause the current song."""

        vc: wavelink.Player = await get_player(ctx)

        await vc.pause()

    @commands.command(name="resume")
    @commands.check(voice_check)
    async def resume_command(self, ctx: commands.Context):
        """Resume the current song."""

        vc: wavelink.Player = await get_player(ctx)

        await vc.resume()

    @commands.command(name="now_playing", aliases=["np"])
    async def now_playing_command(self, ctx: commands.Context):
        """Show the current song."""

        vc: wavelink.Player = await get_player(ctx)

        if not vc.track:
            return await ctx.send("Nothing playing!")

        return await ctx.send(
            f"Now playing: {vc.track}\n{vc.position}/{vc.track.duration}"
        )

    @commands.command(name="volume", aliases=["vol"])
    @commands.check(voice_check)
    async def volume_command(self, ctx: commands.Context, *, vol: int):
        """Change the player volume."""

        vc: wavelink.Player = await get_player(ctx)

        if not 0 < vol < 201:
            return await ctx.send("Volume must be between 1 and 200.")

        await vc.set_volume(vol)
        return await ctx.send(f"Set the volume to {vol}.")


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
