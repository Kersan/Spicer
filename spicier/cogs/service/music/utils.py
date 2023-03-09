from io import BytesIO
from typing import Union

import wavelink
from discord import File, Guild, VoiceChannel
from discord.ext import commands
from PIL import Image

from spicier.errors import PlayerNotPlaying


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


async def player_check(ctx: commands.Context) -> bool:
    """Check: Player is playing"""
    if not await bot_connected(ctx):
        return False
    if not ctx.voice_client.is_playing():
        raise PlayerNotPlaying
    return True


async def player_alive(player: wavelink.Player) -> bool:
    return bool(not player.queue.is_empty or player.track)


def get_time(seconds: Union[int, float]) -> str:
    """Convert seconds to hours, minutes and seconds."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    return f"{int(minutes):02d}:{int(seconds):02d}"


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


def get_lenght(tracks: list[wavelink.Track]) -> str:
    """Get the total length of the queue."""
    return get_time(sum(track.length for track in tracks))


def get_proggres_bar(position, duration) -> File:
    final = _build_progres_bar(position, duration)

    with BytesIO() as image_binary:
        final.save(image_binary, "png")
        image_binary.seek(0)

        return File(fp=image_binary, filename="progress.png")


def _build_progres_bar(position, duration) -> Image:
    background_image = Image.open("img/background.png")
    progress_image = Image.open("img/progress.png")

    progress_width = int((position / duration) * background_image.width)

    progress_bar_crop = progress_image.crop(
        (0, 0, progress_width, progress_image.height)
    )

    final = background_image.copy()
    final.paste(progress_bar_crop, (0, 0))

    return final
