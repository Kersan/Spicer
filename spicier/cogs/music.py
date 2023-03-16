import asyncio
import logging
from typing import Optional, Union

import wavelink
from discord import VoiceChannel, VoiceState
from discord.ext import commands, tasks
from wavelink.abc import Playable

from spicier.config import Config
from spicier.manager import ServerManager

from .service import CustomFilters, MusicService, utils

music_logger = logging.getLogger("spicier.music")


class MusicCog(commands.Cog, MusicService):
    """Handles music functionality for the bot."""

    server_manager: ServerManager
    config: Config
    bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        self.server_manager = bot.server_manager
        self.config = bot.config
        self.bot = bot

        super().__init__(bot, CustomFilters(), music_logger)

        bot.loop.create_task(self.create_nodes(self.config.lavalink))

    @commands.command(name="connect", aliases=["join"])
    @commands.check(utils.user_connected)
    async def connect_command(
        self, ctx: commands.Context, *, channel: VoiceChannel = None
    ):
        """
        Connect to a voice channel.
        """
        vc: wavelink.Player = await self.handler.connect(ctx, channel=channel)
        return await self.message_connected(ctx, vc)

    @commands.command(name="disconnect", aliases=["leave"])
    @commands.check(utils.voice_check)
    async def disconnect_command(self, ctx: commands.Context):
        """
        Disconnect from a voice channel.
        """
        channel = await self.handler.disconnect(ctx)
        return await self.message_disconnected(ctx, channel)

    @commands.command(name="play", aliases=["p"])
    @commands.check(utils.user_connected)
    async def play_command(
        self,
        ctx: commands.Context,
        *,
        track: Union[wavelink.YouTubeTrack, wavelink.YouTubePlaylist] = None,
    ):
        """
        Play a song* with the given search query.
        """
        tracks, vc = await self.handler.play(
            ctx,
            track,
            self.resume_command,
            self.connect_command,
        ) or (None, None)

        if not any((tracks, vc)):
            return

        if not vc.track:
            now = vc.queue.get()
            await vc.play(now)

        if len(tracks) < 2:
            return await self.message_play_single(ctx, vc, tracks[0])

        return await self.message_play_multiple(ctx, vc, tracks)

    @commands.group(name="queue", aliases=["q"])
    @commands.check(utils.player_check)
    async def queue_group(self, ctx: commands.Context, arg: Optional[int] = 0):
        """
        Show the current queue.
        """
        current, queue, file = await self.handler.queue(ctx)

        if not queue or not current:
            return await self.message_queue_is_empty(ctx)

        if arg > len(queue):
            arg = max([0, len(queue) - 10])

        return await self.message_queue(ctx, current, queue, arg, file)

    @queue_group.command(name="clear", aliases=["reset"])
    async def queue_clear_command(self, ctx: commands.Context):
        """
        Clear the current queue.
        """
        return await self.clear_command(ctx)

    @commands.command(name="clear", aliases=["reset"])
    @commands.check(utils.voice_check)
    async def clear_command(self, ctx: commands.Context):
        """
        Clear the current queue.
        """
        vc: wavelink.Player = await utils.get_player(ctx)
        vc.queue.clear()

        return await self.message_queue_cleared(ctx)

    @commands.command(name="skip", aliases=["s", "next"])
    @commands.check(utils.player_check)
    async def skip_command(self, ctx: commands.Context, arg: Optional[str]):
        """
        Skip the current song.
        """
        prev_track, next_track = await self.handler.skip(
            ctx, self.force_skip_command, self.skip_all_command, arg=arg
        )

        if next_track:
            return await self.message_skipped_next(ctx, prev_track, next_track)

        return await self.message_skipped(ctx, prev_track)

    @commands.command(name="skip_all", aliases=["as"])
    @commands.check(utils.voice_check)
    async def skip_all_command(self, ctx: commands.Context):
        """
        Skip all songs in the queue.
        """
        old_queue = await self.handler.skip_all(ctx)
        return await self.message_skip_all(ctx, old_queue)

    @commands.command(name="force_skip", aliases=["fs"])
    @commands.check(utils.voice_check)
    async def force_skip_command(self, ctx: commands.Context):
        """
        Force skip the current song.
        """
        prev_track = await self.handler.force_skip(ctx)
        return await self.message_skipped(ctx, prev_track)

    @commands.command(name="pause", aliases=["stop"])
    @commands.check(utils.voice_check)
    async def pause_command(self, ctx: commands.Context):
        """
        Pause the current song.
        """
        await self.handler.pause(ctx)
        return await ctx.message.add_reaction("⏸")

    @commands.command(name="resume")
    @commands.check(utils.voice_check)
    async def resume_command(self, ctx: commands.Context):
        """
        Resume the current song.
        """
        await self.handler.resume(ctx)
        return await ctx.message.add_reaction("▶")

    @commands.command(name="now_playing", aliases=["np"])
    @commands.check(utils.player_check)
    async def now_playing_command(self, ctx: commands.Context):
        """
        Show the current song.
        """
        vc, image = await self.handler.now_playing(ctx)

        if not vc:
            return await self.message_no_track(ctx)

        return await self.message_now_playing(ctx, vc, image)

    @commands.command(name="volume", aliases=["vol", "v"])
    @commands.check(utils.voice_check)
    async def volume_command(self, ctx: commands.Context, vol: int = None):
        """
        Change the player volume."
        """
        vc = await self.handler.volume(ctx, vol)

        if not vol:
            return await self.message_volume_current(ctx, vc.volume)

        return await self.message_volume(ctx, vc.volume)

    @commands.command(name="seek")
    @commands.check(utils.player_check)
    async def seek_command(self, ctx: commands.Context, *, time: str):
        """
        Seek to a specific time in the current song.
        """
        prev, next, vc = await self.handler.seek(ctx, time)
        return await self.message_seek(ctx, prev, next, vc)

    @commands.group(name="filter", aliases=["filters"])
    async def filter_group(self, ctx: commands.Context):
        """
        Filter group.
        """
        if not ctx.invoked_subcommand:
            return await ctx.send_help(ctx.command)

    @filter_group.command(name="list")
    async def filter_list_command(self, ctx: commands.Context):
        """
        List all available filters.
        """
        return await self.message_filter_list(ctx)

    @filter_group.command(name="set")
    @commands.check(utils.player_check)
    async def filter_set_command(
        self,
        ctx: commands.Context,
        mode: str,
    ):
        """
        Set the filter mode.
        """
        await self.handler.filter(ctx, mode=mode)

        return await self.message_filter_set(ctx, mode)

    @filter_group.command(name="reset", aliases=["clear"])
    @commands.check(utils.player_check)
    async def filter_reset_command(self, ctx: commands.Context):
        """
        Reset the filter mode.
        """
        await self.handler.filter_reset(ctx)
        return await self.message_filter_clear(ctx)

    @filter_group.command(name="current", aliases=["show"])
    @commands.check(utils.player_check)
    async def filter_current_command(self, ctx: commands.Context):
        """
        Show the current filter mode.
        """
        filter, description = await self.handler.filter_current(ctx)

        return await self.message_filter_current(ctx, filter, description)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        music_logger.info(f"Node: <{node.identifier}> is ready!")

    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self, player: wavelink.Player, track: wavelink.Track, reason
    ):
        channel = self.bot.get_channel(
            await self.server_manager.get_channel(player.guild.id)
        )

        if player.track:
            return

        if player.queue.is_empty:
            return await self.message_queue_empty(channel)

        next: Playable = player.queue.get()
        await player.play(next)

        return await self.message_next_track(channel, player, next)

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
        if not voice:
            return

        if len(voice.channel.members) > 1:
            return

        try:
            await player.disconnect()
        except Exception:
            pass

    @dead.before_loop
    async def before_disconnect(self):
        await asyncio.sleep(self.config.leave_time)


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
