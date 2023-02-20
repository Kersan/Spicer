import re
from typing import Callable, Union

import wavelink
from discord import VoiceChannel
from discord.ext import commands
from discord.ext.commands import Parameter
from wavelink.queue import WaitQueue

from spicier.errors import (
    QueueEmpty,
    SearchNotFound,
    VoiceConnectionError,
    WrongArgument,
    VolumeBelowZero
)

from . import CustomFilters, utils


class MusicHandlers:
    def __init__(self, filters: CustomFilters):
        self.filters = filters

    async def handle_connect(
        self, ctx: commands.Context, channel: VoiceChannel = None
    ) -> wavelink.Player:
        if channel and channel.guild != ctx.guild:
            raise WrongArgument(message="Channel not found.")

        try:
            vc: wavelink.Player = await utils.get_player(channel or ctx)
            await vc.connect(cls=wavelink.Player)
        except AttributeError:
            raise VoiceConnectionError()

        finally:
            return vc

    async def handle_disconnect(self, ctx: commands.Context) -> str:
        vc: wavelink.Player = await utils.get_player(ctx)

        if vc.queue:
            vc.queue.clear()

        channel_name = vc.channel.name

        await ctx.voice_client.disconnect()
        return channel_name

    async def handle_play(
        self,
        ctx: commands.Context,
        track: Union[str, wavelink.Track],
        connect: Callable,
        resume: Callable,
    ):

        if not await utils.bot_connected(ctx) and not track:
            await connect(ctx)
            return (None, None)

        tracks = []
        vc = await utils.get_player(ctx)

        if not track and vc.is_paused() and vc.track:
            return await resume(ctx)

        if not track and not vc.is_paused():
            raise commands.MissingRequiredArgument(
                Parameter("Track", Parameter.POSITIONAL_OR_KEYWORD)
            )

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
                raise WrongArgument(message="Invalid search query.")

        if not tracks:
            raise SearchNotFound(track)

        for t in tracks:
            vc.queue.put(t)

        return tracks, vc

    async def handle_queue(
        self,
        ctx: commands.Context,
    ) -> tuple[wavelink.Track, WaitQueue]:
        vc: wavelink.Player = await utils.get_player(ctx)

        return vc.track, vc.queue

    async def handle_skip(
        self,
        ctx: commands.Context,
        force_skip: Callable,
        skip_all: Callable,
        arg: str = None,
    ) -> wavelink.Track:
        vc: wavelink.Player = await utils.get_player(ctx)

        arg_all = ["all", "a"]
        arg_force = ["force", "f"]

        if arg and arg.lower() not in arg_all + arg_force:
            raise WrongArgument(message="Invalid argument provided.")

        if arg and arg.lower() in arg_all:
            return await skip_all(ctx)

        if arg and arg.lower() in arg_force:
            return await force_skip(ctx)

        track = vc.track
        next = None

        if not vc.queue:
            await vc.stop()

        else:
            next = vc.queue.get()
            await vc.play(next)

        return track, next

    async def handle_pause(self, ctx: commands.Context) -> None:
        vc: wavelink.Player = await utils.get_player(ctx)
        await vc.pause()

    async def handle_resume(self, ctx: commands.Context) -> None:
        vc: wavelink.Player = await utils.get_player(ctx)
        await vc.resume()

    async def handle_now_playing(self, ctx: commands.Context) -> wavelink.Player:
        vc: wavelink.Player = utils.get_player(ctx)
        
        if not vc.track:
            return None
        return vc

    async def handle_volume(self, ctx: commands.Context, vol) -> wavelink.Player:
        vc: wavelink.Player = await utils.get_player(ctx)
        
        if not vol:
            return vc

        if not 0 < vol < 201:
            raise VolumeBelowZero

        await vc.set_volume(vol)
        return vc


    async def handle_skip_all(self, ctx: commands.Context) -> WaitQueue:
        vc: wavelink.Player = await utils.get_player(ctx)

        if not vc.queue or vc.queue.is_empty:
            raise QueueEmpty("Queue is already empty.")

        old_queue = vc.queue

        vc.queue.clear()
        await vc.stop()

        return old_queue

    async def handle_force_skip(self, ctx: commands.Context) -> wavelink.Track:
        vc: wavelink.Player = await utils.get_player(ctx)

        if not vc.queue or vc.queue.is_empty:
            raise QueueEmpty("Queue is already empty.")

        track = vc.track
        await vc.stop()

        if vc.queue and not vc.track:
            vc.play(vc.queue.get())

        return track

    async def handle_seek(self, ctx: commands.Context, time: str) -> tuple[str, str, wavelink.Track]:
        vc: wavelink.Player = await utils.get_player(ctx)
        prev_pos = get_time(vc.track.possition)

        if time.isdigit() and int(time) < vc.track.duration and int(time) > 0:
            position = int(time)
            await vc.seek(position * 1000)
            return prev_pos, utils.get_time(position), vc.track

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
        return prev_pos, utils.get_time(position), vc.track

    async def handle_filter(self, vc: wavelink.Player, mode: str):

        if not mode in self.filters.modes.keys():
            raise WrongArgument("Invalid filter mode.")

        await vc.set_filter(self.filters.modes[mode])
