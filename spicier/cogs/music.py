import asyncio
import logging
from typing import Optional, Union

import wavelink
from discord import VoiceChannel, VoiceState
from discord.ext import commands, tasks
from wavelink.abc import Playable

from .service import (
    MusicService,
    bot_connected,
    get_player,
    player_alive,
    user_connected,
    voice_check,
)


class MusicCog(commands.Cog, MusicService):
    def __init__(self, bot: commands.Bot):
        self.config = bot.config
        self.bot = bot

        super().__init__(bot)

        bot.loop.create_task(self.create_nodes(self.config.lavalink))

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        logging.info(f"Node: <{node.identifier}> is ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self, player: wavelink.Player, track: wavelink.Track, reason
    ):
        if player.track:
            return

        if player.queue.is_empty:
            # TODO: Get queue text channel and send message
            return

        next: Playable = player.queue.get()
        await player.play(next)

        # TODO: Get queue text channel and send message

    @commands.command(name="connect", aliases=["join"])
    @commands.check(user_connected)
    async def connect_command(
        self, ctx: commands.Context, *, channel: VoiceChannel = None
    ):
        """Connect to a voice channel."""
        if ctx.voice_client and not self.is_alone(ctx):
            return await ctx.send("I'm already in a voice channel.")

        if await voice_check(ctx):
            return await ctx.send("Jestem z tobą już wariacie 😎")

        return await self.handle_connect(ctx, channel=channel)

    @commands.command(name="disconnect", aliases=["leave"])
    @commands.check(voice_check)
    async def disconnect_command(self, ctx: commands.Context):
        """Disconnect from a voice channel."""
        await self.handle_disconnect(ctx)
        return await ctx.send("Disconnected.")

    @commands.command()
    @commands.check(user_connected)
    async def play(
        self,
        ctx: commands.Context,
        *,
        track: Union[wavelink.YouTubeTrack, wavelink.YouTubePlaylist, str, None],
    ):
        """Play a song* with the given search query."""

        tracks, vc = await self.handle_play(
            ctx=ctx,
            track=track,
            connect=self.connect_command,
            resume=self.resume_command,
        ) or (None, None)

        if not vc or not tracks:
            return

        final = tracks[0]

        if not vc.track:
            now = vc.queue.get()
            await vc.play(now)

            # TODO: Handle this message better 😪
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

        queue = await self.handle_queue(
            ctx, clear=self.clear_command, now_playing=self.now_playing_command, arg=arg
        )

        if not queue:
            return await ctx.send("No songs queued.")

        display = "\n".join(f"{i} - {t.title}" for i, t in enumerate(queue, start=1))
        await ctx.send(f"Kolejka: ```{display}```")

    @commands.command(name="clear", aliases=["reset"])
    @commands.check(voice_check)
    async def clear_command(self, ctx: commands.Context):
        """Clear the current queue."""

        vc: wavelink.Player = await get_player(ctx)
        vc.queue.clear()

        await ctx.send("Cleared the queue!")

    @commands.command(name="skip", aliases=["s"])
    @commands.check(voice_check)
    async def skip_command(self, ctx: commands.Context, arg: Optional[str]):
        """Skip the current song."""

        vc: wavelink.Player = await self.handle_skip(
            ctx, self.force_skip_command, self.skip_all_command, arg
        )

        if vc.queue:
            await vc.play(vc.queue.get())

    @commands.command(name="skip_all", aliases=["as"])
    @commands.check(voice_check)
    async def skip_all_command(self, ctx: commands.Context):
        """Skip all songs in the queue."""

        await self.handle_skip_all(ctx)
        return await ctx.send("Skipped all songs!")

    @commands.command(name="force_skip", aliases=["fs"])
    @commands.check(voice_check)
    async def force_skip_command(self, ctx: commands.Context):
        """Force skip the current song."""

        vc: wavelink.Player = await self.handle_force_skip(ctx)

        if vc.queue and not vc.track:
            vc.play(vc.queue.get())

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

    @commands.command(name="volume", aliases=["vol", "v"])
    @commands.check(voice_check)
    async def volume_command(self, ctx: commands.Context, *, vol: int = None):
        """Change the player volume."""

        vc: wavelink.Player = await get_player(ctx)

        if not vol:
            return await ctx.send(f"Current volume: {vc.volume}")

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
        if voice and len(voice.channel.members) == 1:
            try:
                await player.disconnect()
            except Exception:
                pass

    @dead.before_loop
    async def before_disconnect(self):
        await asyncio.sleep(self.config.leave_time)


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
