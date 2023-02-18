from typing import Callable, Union

import wavelink
from discord import Guild, VoiceChannel
from discord.ext import commands
from discord.ext.commands import Parameter
from wavelink.errors import NodeOccupied
from wavelink.queue import WaitQueue

from spicier.errors import QueueEmpty, SearchNotFound, VoiceConnectionError


async def user_connected(ctx: commands.Context) -> bool:
    """Check: User connected to voice channel"""
    return bool(ctx.author.voice)


async def bot_connected(ctx: commands.Context) -> bool:
    """Check: Bot connected to voice channel"""
    return bool(ctx.voice_client)


async def voice_check(ctx: commands.Context) -> bool:
    """Check: User and bot connected to same voice channel"""
    if not await user_connected(ctx):
        return False
    if not await bot_connected(ctx):
        return False
    if ctx.author.voice.channel == ctx.voice_client.channel:
        return True
    return False


async def player_alive(player: wavelink.Player) -> bool:
    return bool(not player.queue.is_empty or player.track)


async def get_player(
    case: Union[commands.Context, Guild, VoiceChannel]
) -> wavelink.Player:
    """Get the player for the guild."""
    if isinstance(case, Guild):
        return wavelink.NodePool.get_node().get_player(case)

    if not case.voice_client and isinstance(case, VoiceChannel):
        return await case.connect(cls=wavelink.Player)

    return case.voice_client or await case.author.voice.channel.connect(
        cls=wavelink.Player
    )


class MusicService:
    def __init__(self, bot):
        self.bot = bot

    async def create_nodes(self, config):
        try:
            await self.bot.wait_until_ready()
            await wavelink.NodePool.create_node(bot=self.bot, **config)
        except NodeOccupied:
            pass

    async def handle_connect(
        self, ctx: commands.Context, channel: VoiceChannel = None
    ) -> wavelink.Player:
        if channel and channel.guild != ctx.guild:
            raise commands.BadArgument("Channel not found.")

        try:
            vc: wavelink.Player = await get_player(channel or ctx)
            await vc.connect(cls=wavelink.Player)
        except AttributeError:
            raise VoiceConnectionError()

        finally:
            return vc

    async def handle_disconnect(self, ctx: commands.Context):
        vc: wavelink.Player = await get_player(ctx)

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

        if not await bot_connected(ctx) and not track:
            await connect(ctx)
            return (None, None)

        tracks = []
        vc = await get_player(ctx)

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
                raise commands.BadArgument()

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
            raise commands.BadArgument("Invalid argument provided.")

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
    ) -> wavelink.Player:
        vc: wavelink.Player = await get_player(ctx)

        arg_all = ["all", "a"]
        arg_force = ["force", "f"]

        if arg and arg.lower() not in arg_all + arg_force:
            raise commands.BadArgument("Invalid argument provided.")

        if arg and arg.lower() in arg_all:
            await skip_all(ctx)

        if arg and arg.lower() in arg_force:
            await force_skip(ctx)

        if not vc.queue:
            await vc.stop()

        return vc

    async def handle_skip_all(self, ctx: commands.Context) -> None:
        vc: wavelink.Player = await get_player(ctx)

        if not vc.queue or vc.queue.is_empty:
            raise QueueEmpty("Queue is already empty.")

        vc.queue.clear()
        await vc.stop()

    async def handle_force_skip(self, ctx: commands.Context) -> wavelink.Player:
        vc: wavelink.Player = await get_player(ctx)

        if not vc.queue or vc.queue.is_empty:
            raise QueueEmpty("Queue is already empty.")

        await vc.stop()

    def is_alone(ctx: commands.Context) -> bool:
        return len(ctx.voice_client.channel.members) == 1
