from typing import Union

import wavelink
from discord import Guild, VoiceChannel
from discord.ext import commands

from .filters import CustomFilters


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


def get_time(seconds: Union[int, float]) -> str:
    """Convert seconds to minutes and seconds."""
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes)}:{int(seconds):02}"


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

