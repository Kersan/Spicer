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

    async def handle_disconnect(self, ctx: commands.Context):
        vc: wavelink.Player = await utils.get_player(ctx)

        if vc.queue:
            vc.queue.clear()

        await ctx.voice_client.disconnect()

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
        clear: Callable,
        now_playing: Callable,
        arg: str = None,
    ) -> WaitQueue:
        clear = ["clear", "c", "reset", "r"]

        vc: wavelink.Player = ctx.voice_client

        if arg and arg.lower() not in clear:
            raise WrongArgument(message="Invalid argument provided.")

        if arg and arg.lower() in clear:
            await clear(ctx)
            return

        if vc.track and not vc.queue.is_empty:
            await now_playing(ctx)

        return vc.queue

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

        if not vc.queue:
            await vc.stop()

        else:
            await vc.play(vc.queue.get())

        return track

    async def handle_skip_all(self, ctx: commands.Context) -> None:
        vc: wavelink.Player = await utils.get_player(ctx)

        if not vc.queue or vc.queue.is_empty:
            raise QueueEmpty("Queue is already empty.")

        vc.queue.clear()
        await vc.stop()

    async def handle_force_skip(self, ctx: commands.Context) -> wavelink.Track:
        vc: wavelink.Player = await utils.get_player(ctx)

        if not vc.queue or vc.queue.is_empty:
            raise QueueEmpty("Queue is already empty.")

        track = vc.track
        await vc.stop()

        if vc.queue and not vc.track:
            vc.play(vc.queue.get())

        return track

    async def handle_seek(self, vc: wavelink.Player, time: str) -> str:
        if time.isdigit() and int(time) < vc.track.duration and int(time) > 0:
            position = int(time)
            await vc.seek(position * 1000)
            return utils.get_time(position)

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
        return utils.get_time(position)

    async def handle_filter(self, vc: wavelink.Player, mode: str):

        if not mode in self.filters.modes.keys():
            raise WrongArgument("Invalid filter mode.")

        await vc.set_filter(self.filters.modes[mode])
