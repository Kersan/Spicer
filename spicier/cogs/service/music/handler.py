import logging
import re
from typing import Callable, Union

import wavelink
from discord import File, VoiceChannel
from discord.ext import commands
from discord.ext.commands import Parameter
from wavelink.queue import WaitQueue

from spicier.errors import (
    QueueEmpty,
    SearchNotFound,
    VoiceConnectionError,
    VolumeBelowZero,
    WrongArgument,
)

from . import CustomFilters, utils


def use_vc(func: Callable) -> Callable:
    async def wrapper(self, ctx: commands.Context, *args, **kwargs):
        vc = await utils.get_player(ctx)
        return await func(self, ctx, vc=vc, *args, **kwargs)

    return wrapper


class CommandArgs:
    def __init__(self):
        self.all = ["all", "a"]
        self.force = ["force", "f"]
        self.loop = ["loop", "l"]


class MusicHandler:
    def __init__(self, filters: CustomFilters):
        self.filters = filters

        self.args = CommandArgs()

    async def _youtube_search(self, query: str):
        result = await wavelink.YouTubeTrack.search(query=query, return_first=True)

        if not result:
            raise SearchNotFound(query)

        return result

    async def play(
        self,
        ctx: commands.Context,
        track: Union[str, wavelink.abc.Playable],
        resume: Callable,
        connect: Callable,
    ):
        logging.info(f"Handling play command with track: {track}")

        if not await utils.bot_connected(ctx) and not track:
            await connect(ctx)
            return

        vc = await utils.get_player(ctx)

        if not track and vc.is_paused() and vc.track:
            return await resume(ctx)

        if not track and not vc.is_paused():
            raise commands.MissingRequiredArgument(
                Parameter("Track", Parameter.POSITIONAL_OR_KEYWORD)
            )

        tracks = []
        if isinstance(track, wavelink.YouTubeTrack):
            tracks.append(track)

        if isinstance(track, wavelink.YouTubePlaylist):
            tracks.extend([t for t in track.tracks])

        elif isinstance(track, str):
            try:
                tracks.append(await self._youtube_search(track))
            except Exception:
                raise WrongArgument(message="Invalid search query.")

        if not tracks:
            raise SearchNotFound(track)

        for t in tracks:
            vc.queue.put(t)

        return tracks, vc

    async def connect(
        self, ctx: commands.Context, channel: VoiceChannel = None
    ) -> wavelink.Player:
        if await utils.voice_check(ctx):
            raise VoiceConnectionError("Already in voice channel.")

        if ctx.voice_client and not self.is_alone(ctx):
            raise VoiceConnectionError("In voice channel with someone.")

        if channel and channel.guild != ctx.guild:
            raise WrongArgument(message="Channel not found.")

        try:
            vc: wavelink.Player = await utils.get_player(channel or ctx)
            await vc.connect(cls=wavelink.Player)
        except AttributeError:
            raise VoiceConnectionError()

        finally:
            return vc

    @use_vc
    async def disconnect(
        self, ctx: commands.Context, vc: wavelink.Player = None
    ) -> str:
        if vc.queue:
            vc.queue.clear()

        channel_name = vc.channel.name

        await ctx.voice_client.disconnect()
        return channel_name

    @use_vc
    async def queue(
        self, ctx: commands.Context, vc: wavelink.Player = None
    ) -> tuple[wavelink.Track, WaitQueue, File]:
        file = None
        if vc.track:
            file = utils.get_proggres_bar(vc.position, vc.track.duration)

        return (vc.track, vc.queue, file)

    async def _handle_skip_arg(self, ctx, arg, force_skip, skip_all):
        if arg.lower() in self.args.all:
            return await skip_all(ctx)

        if arg.lower() in self.args.force:
            return await force_skip(ctx)

        raise WrongArgument(message="Invalid argument provided.")

    @use_vc
    async def skip(
        self,
        ctx: commands.Context,
        force_skip: commands.Command,
        skip_all: commands.Command,
        arg: str = None,
        vc: wavelink.Player = None,
    ) -> wavelink.Track:
        if arg:
            return await self._handle_skip_arg(ctx, arg, force_skip, skip_all)

        prev = vc.track
        next = None

        if vc.queue:
            next = vc.queue.get()
            await vc.play(next)

        else:
            await vc.stop()

        return prev, next

    @use_vc
    async def pause(self, ctx: commands.Context, vc: wavelink.Player = None) -> None:
        await vc.pause()

    @use_vc
    async def resume(self, ctx: commands.Context, vc: wavelink.Player = None) -> None:
        await vc.resume()

    @use_vc
    async def now_playing(
        self, ctx: commands.Context, vc: wavelink.Player = None
    ) -> tuple[wavelink.Player, File]:
        file = utils.get_proggres_bar(vc.position, vc.track.duration)

        if not vc.track:
            return (None, None)
        return (vc, file)

    @use_vc
    async def volume(
        self, ctx: commands.Context, vol, vc: wavelink.Player = None
    ) -> wavelink.Player:
        if not vol:
            return vc

        if not 0 < vol < 201:
            raise VolumeBelowZero

        await vc.set_volume(vol)
        return vc

    @use_vc
    async def skip_all(
        self, ctx: commands.Context, vc: wavelink.Player = None
    ) -> WaitQueue:
        if not vc.queue or vc.queue.is_empty:
            raise QueueEmpty("Queue is already empty.")

        old_queue = vc.queue

        vc.queue.clear()
        await vc.stop()

        return old_queue

    @use_vc
    async def force_skip(
        self, ctx: commands.Context, vc: wavelink.Player = None
    ) -> wavelink.Track:
        if not vc.queue or vc.queue.is_empty:
            raise QueueEmpty("Queue is already empty.")

        track = vc.track
        await vc.stop()

        if vc.queue and not vc.track:
            vc.play(vc.queue.get())

        return track

    async def seek(
        self, ctx: commands.Context, time: str
    ) -> tuple[str, str, wavelink.Player]:
        vc: wavelink.Player = await utils.get_player(ctx)
        prev_pos = vc.position

        if time.isdigit() and int(time) < vc.track.duration and int(time) >= 0:
            position = int(time)
            await vc.seek(position * 1000)
            return prev_pos, position, vc

        elif time.isdigit():
            raise WrongArgument(message="Given time must be inside <0, song duration>.")

        if not (match := re.match(r"(\d{1,2}):(\d{2})", time)):
            raise WrongArgument(message="Invalid time format. Use mm:ss. or seconds.")

        minutes, seconds = map(int, match.groups())

        if minutes > vc.track.duration // 60:
            raise WrongArgument(message="Minutes must be less than the song duration.")

        if seconds > 59:
            raise WrongArgument(message="Seconds must be less than 60.")

        position = minutes * 60 + seconds

        await vc.seek(position * 1000)
        return prev_pos, position, vc

    @use_vc
    async def filter(
        self, ctx: commands.Context, mode: str, vc: wavelink.Player = None
    ):
        if mode not in self.filters.modes.keys():
            raise WrongArgument("Invalid filter mode.")

        await vc.set_filter(self.filters.modes[mode])

    @use_vc
    async def filter_reset(self, ctx: commands.Context, vc: wavelink.Player = None):
        await vc.set_filter(self.filters.clear, seek=True)

    @use_vc
    async def filter_current(self, ctx: commands.Context, vc: wavelink.Player = None):
        filter = vc.filter.name if vc.filter else None
        return (
            filter,
            self.filters.modes[filter].description
            if filter
            else "Ten filtr nie posiada opisu.",
        )
