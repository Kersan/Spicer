import asyncio
import logging
from typing import Literal, Optional, Union

import wavelink
from discord import VoiceChannel, VoiceState
from discord.ext import commands, tasks
from wavelink.abc import Playable

from spicier.cogs.embeds import MusicEmbed

from .service import CustomFilters, MusicService, utils


class MusicCog(commands.Cog, MusicService):
    def __init__(self, bot: commands.Bot):
        self.config = bot.config
        self.bot = bot
        self.filters = CustomFilters()

        super().__init__(bot, self.filters)

        bot.loop.create_task(self.create_nodes(self.config.lavalink))

    @commands.command(name="connect", aliases=["join"])
    @commands.check(utils.user_connected)
    async def connect_command(
        self, ctx: commands.Context, *, channel: VoiceChannel = None
    ):
        """Connect to a voice channel."""
        if await utils.voice_check(ctx):
            return await self.message_already_with(ctx)

        if ctx.voice_client and not self.is_alone(ctx):
            return self.message_already_connected(ctx)

        vc: wavelink.Player = await self.handle_connect(ctx, channel=channel)
        return await self.message_connected(ctx, vc)

    @commands.command(name="disconnect", aliases=["leave"])
    @commands.check(utils.voice_check)
    async def disconnect_command(self, ctx: commands.Context):
        """Disconnect from a voice channel."""
        channel = await self.handle_disconnect(ctx)
        return self.message_disconnected(ctx, channel)

    @commands.command()
    @commands.check(utils.user_connected)
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

        final: wavelink.Track = tracks[0]

        if not vc.track:
            now = vc.queue.get()
            await vc.play(now)

        return (
            await self.message_play_single(ctx, vc, final)
            if len(tracks) < 2
            else await self.message_play_multiple(ctx, vc, tracks)
        )

    @commands.group(name="queue", aliases=["q"])
    @commands.check(utils.player_check)
    async def queue_group(self, ctx: commands.Context, arg: Optional[int] = 0):
        """Show the current queue."""

        current, queue = await self.handle_queue(ctx)

        if not queue or not current:
            return await self.message_queue_is_empty(ctx)

        if arg > len(queue):
            arg = max([0, len(queue) - 10])

        return await self.message_queue(ctx, current, queue, arg)

    @queue_group.command(name="clear", aliases=["reset"])
    async def queue_clear_command(self, ctx: commands.Context):
        """Clear the current queue."""

        return await self.clear_command(ctx)

    @commands.command(name="clear", aliases=["reset"])
    @commands.check(utils.voice_check)
    async def clear_command(self, ctx: commands.Context):
        """Clear the current queue."""

        vc: wavelink.Player = await utils.get_player(ctx)
        vc.queue.clear()

        return await self.message_queue_cleared(ctx)

    @commands.command(name="skip", aliases=["s", "next"])
    @commands.check(utils.player_check)
    async def skip_command(self, ctx: commands.Context, arg: Optional[str]):
        """Skip the current song."""

        prev_track, next_track = await self.handle_skip(
            ctx, self.force_skip_command, self.skip_all_command, arg
        )

        if next_track:
            return await self.message_skipped_next(ctx, prev_track, next_track)

        return await self.message_skipped(ctx, prev_track)

    @commands.command(name="skip_all", aliases=["as"])
    @commands.check(utils.voice_check)
    async def skip_all_command(self, ctx: commands.Context):
        """Skip all songs in the queue."""

        await self.handle_skip_all(ctx)
        return await ctx.send("Skipped all songs!")

    @commands.command(name="force_skip", aliases=["fs"])
    @commands.check(utils.voice_check)
    async def force_skip_command(self, ctx: commands.Context):
        """Force skip the current song."""

        prev_track = await self.handle_force_skip(ctx)
        return await ctx.send(f"Skipped {prev_track.title}!")

    @commands.command(name="pause", aliases=["stop"])
    @commands.check(utils.voice_check)
    async def pause_command(self, ctx: commands.Context):
        """Pause the current song."""

        vc: wavelink.Player = await utils.get_player(ctx)
        await vc.pause()
        return await ctx.message.add_reaction("⏸")

    @commands.command(name="resume")
    @commands.check(utils.voice_check)
    async def resume_command(self, ctx: commands.Context):
        """Resume the current song."""

        vc: wavelink.Player = await utils.get_player(ctx)
        await vc.resume()
        return await ctx.message.add_reaction("▶")

    @commands.command(name="now_playing", aliases=["np"])
    @commands.check(utils.player_check)
    async def now_playing_command(self, ctx: commands.Context):
        """Show the current song."""

        vc: wavelink.Player = await utils.get_player(ctx)

        return await ctx.send(
            f"Now playing: {vc.track}\n{utils.get_time(vc.position)} - {utils.get_time(vc.track.duration)}"
        )

    @commands.command(name="volume", aliases=["vol", "v"])
    @commands.check(utils.voice_check)
    async def volume_command(self, ctx: commands.Context, *, vol: int = None):
        """Change the player volume."""

        vc: wavelink.Player = await utils.get_player(ctx)

        if not vol:
            return await ctx.send(f"Current volume: {vc.volume}")

        if not 0 < vol < 201:
            return await ctx.send("Volume must be between 1 and 200.")

        await vc.set_volume(vol)

        return await ctx.send(f"Set the volume to {vol}.")

    @commands.command(name="seek")
    @commands.check(utils.player_check)
    async def seek_command(self, ctx: commands.Context, *, time: str):
        """Seek to a specific time in the current song."""

        vc: wavelink.Player = await utils.get_player(ctx)

        message = await self.handle_seek(vc, time)
        return await ctx.send(f"Seeked to {message}.")

    @commands.group(name="filter")
    async def filter_group(self, ctx: commands.Context):
        """Filter group."""
        if not ctx.invoked_subcommand:
            return await ctx.send_help(ctx.command)

    @filter_group.command(name="list")
    async def filter_list_command(self, ctx: commands.Context):
        """List all available filters."""

        return await ctx.send(
            f"Available filters: ```{', '.join(self.filters.modes.keys())}```"
        )

    @filter_group.command(name="set")
    @commands.check(utils.player_check)
    async def filter_set_command(
        self,
        ctx: commands.Context,
        *,
        mode: Literal[
            "boost", "piano", "metal", "flat", "spin", "nightcore", "destroy"
        ],
    ):
        """Set the filter mode."""
        vc: wavelink.Player = await utils.get_player(ctx)

        await self.handle_filter(vc, mode)

        return await ctx.send(f"Set the filter mode to {mode}.")

    @filter_group.command(name="reset", aliases=["clear"])
    @commands.check(utils.player_check)
    async def filter_reset_command(self, ctx: commands.Context):
        """Reset the filter mode."""

        vc: wavelink.Player = await utils.get_player(ctx)

        await vc.set_filter(self.filters.clear, seek=True)

    @filter_group.command(name="current", aliases=["show"])
    @commands.check(utils.player_check)
    async def filter_current_command(self, ctx: commands.Context):
        """Show the current filter mode."""

        vc: wavelink.Player = await utils.get_player(ctx)

        return await ctx.send(f"Current filter mode: {vc.filter}")

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

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member, before: VoiceState, after: VoiceState
    ):
        if member.id == self.bot.user.id and after.channel is None:
            player = await utils.get_player(before.channel.guild)
            if player is not None:
                await player.disconnect()

        elif (
            not after.channel
            and self.bot.user in before.channel.members
            and len(before.channel.members) <= 2
        ):
            player = await utils.get_player(before.channel.guild)
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
