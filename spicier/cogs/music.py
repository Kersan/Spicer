import asyncio
import logging
from typing import Optional, Union

import wavelink
from discord import Guild, VoiceChannel, VoiceState
from discord.ext import commands, tasks
from wavelink.errors import NodeOccupied


async def user_connected(ctx: commands.Context):
    """Check if the user is connected to a voice channel."""
    if not ctx.author.voice:
        await ctx.send(
            "You have to be connected to a voice channel to use this command."
        )
        return False
    return True


async def bot_connected(ctx: commands.Context):
    """Check if the bot is connected to a voice channel."""
    if not ctx.voice_client:
        await ctx.send("I am not connected to a voice channel.")
        return False
    return True


async def voice_check(ctx: commands.Context):
    """Check if the bot and user are connected to the same voice channel."""
    if not await user_connected(ctx):
        return False
    if not await bot_connected(ctx):
        return False
    if ctx.author.voice.channel != ctx.voice_client.channel:
        await ctx.send("You have to be in the same voice channel as me.")
        return False
    return True


async def get_player(case: Union[commands.Context, Guild]):
    """Get the player for the guild."""
    if isinstance(case, Guild):
        return wavelink.NodePool.get_node().get_player(case)

    return case.voice_client or await case.author.voice.channel.connect(
        cls=wavelink.Player
    )


class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.create_nodes())

    async def create_nodes(self):
        try:
            await self.bot.wait_until_ready()
            await wavelink.NodePool.create_node(
                bot=self.bot, **self.bot.config.lavalink
            )
        except NodeOccupied:
            pass

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        logging.info(f"Node: <{node.identifier}> is ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self, player: wavelink.Player, track: wavelink.Track, reason
    ):
        if player.track:
            return

        if player.queue.is_empty:
            await asyncio.sleep(300)
            if not player.queue and not player.track:
                await player.disconnect()

        else:
            await player.play(player.queue.get())

    @commands.command(name="connect", aliases=["join"])
    @commands.check(user_connected)
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
    @commands.check(user_connected)
    async def play(
        self,
        ctx: commands.Context,
        *,
        track: Union[wavelink.YouTubeTrack, wavelink.YouTubePlaylist, str, None],
    ):
        """Play a song with the given search query.
        If not connected, connect to our voice channel.

        When the query is a URL, we will attempt to play the song.
        If not, we will attempt to search for a song.
        """

        tracks = []
        vc: wavelink.Player = ctx.voice_client

        if not vc:
            vc = await self.connect_command(ctx, channel=ctx.author.voice.channel)

        if not track and vc.is_paused:
            await vc.resume()
            return await self.resume_command(ctx)

        elif not track:
            raise commands.BadArgument("No track provided.")

        if isinstance(track, wavelink.YouTubeTrack):
            tracks.append(track)

        if isinstance(track, wavelink.YouTubePlaylist):
            tracks.extend([t for t in track.tracks])

        elif isinstance(track, str):
            try:
                result = await wavelink.YouTubeTrack.search(
                    query=track, return_first=True
                )

                if result:
                    tracks.append(result)
            except Exception:
                raise commands.BadArgument(f"Could not find any results for {track}.")

        if not tracks:
            return await ctx.send("No match found!")

        final = tracks[0]
        for t in tracks:
            vc.queue.put(t)

        if not vc.track:
            now = vc.queue.get()
            await vc.play(now)

            await ctx.send(
                f"Added to queue {len(tracks)} songs. \nNow playing: {final.title}"
                if len(tracks) > 1
                else f"Now playing: {final.title}"
            )

        else:
            await ctx.send(
                f"Added to queue {len(tracks)} songs."
                if len(tracks) > 1
                else f"Added {final.title} to queue."
            )

    @commands.command(name="queue", aliases=["q"])
    @commands.check(bot_connected)
    async def queue_command(self, ctx: commands.Context, arg: Optional[str]):
        """Show the current queue."""

        if not ctx.voice_client:
            return await ctx.send("Not playing rn!")

        vc: wavelink.Player = ctx.voice_client

        clear = ["clear", "c", "reset", "r"]

        if arg and arg.lower() not in clear:
            raise commands.BadArgument("Invalid argument provided.")

        if arg and arg.lower() in clear:
            vc.queue.clear()
            return await ctx.send(
                "Cleared queue." if arg.startswith("c") else "Reset queue."
            )

        if vc.track and not vc.queue:
            return await self.now_playing_command(ctx)

        if not vc.queue:
            return await ctx.send("No songs queued!")

        queue = "\n".join(f"{i} - {t.title}" for i, t in enumerate(vc.queue, start=1))
        await ctx.send(f"Now playing: {vc.track}\n```{queue}```")

    @commands.command(name="skip", aliases=["s"])
    @commands.check(voice_check)
    async def skip_command(self, ctx: commands.Context, arg: Optional[str]):
        """Skip the current song."""

        vc: wavelink.Player = await get_player(ctx)

        arg_all = ["all", "a"]
        arg_force = ["force", "f"]

        if arg and arg.lower() not in arg_all + arg_force:
            raise commands.BadArgument("Invalid argument provided.")

        if arg and arg.lower() in arg_all:
            vc.queue.clear()
            await vc.stop()
            return await ctx.send("Skipped all songs!")

        if arg and arg.lower() in arg_force:
            await vc.stop()
            return await ctx.send("Force skipped!")

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
    @commands.check(bot_connected)
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

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member, before: VoiceState, after: VoiceState
    ):
        if member.id == self.bot.user.id and after.channel is None:
            player = await get_player(before.channel.guild)
            if player is not None:
                await player.disconnect()

        elif (
            not after.channel
            and self.bot.user in before.channel.members
            and len(before.channel.members) <= 2
        ):
            player = await get_player(before.channel.guild)
            await self.dead(player, before)

    @tasks.loop(count=1)
    async def dead(self, player: wavelink.Player, voice: VoiceState):
        print(voice.channel.members)
        if voice and len(voice.channel.members) == 1:
            try:
                await player.disconnect()
            except Exception:
                pass

    @dead.before_loop
    async def before_disconnect(self):
        await asyncio.sleep(5)


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
