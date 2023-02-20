from typing import Any

import wavelink
from discord.ext import commands
from wavelink.errors import NodeOccupied
from wavelink.queue import WaitQueue

from ...embeds.music import MusicEmbed
from . import utils
from .handler import MusicHandlers


class MusicService(MusicHandlers):
    """Music Cog Service"""

    def __init__(self, bot, filters):
        self.bot = bot
        self.filters = filters

        super().__init__(filters)

    async def create_nodes(self, config):
        try:
            await self.bot.wait_until_ready()
            await wavelink.NodePool.create_node(bot=self.bot, **config)
        except NodeOccupied:
            pass

    def is_alone(self, ctx: commands.Context) -> bool:
        return len(ctx.voice_client.channel.members) == 1

    async def message_already_with(self, ctx: commands.Context):
        ctx.reply(
            embed=MusicEmbed.success(title="**Jestem już z tobą wariacie 😎**"),
            mention_author=False,
        )

    async def message_already_connected(self, ctx: commands.Context):
        embed = MusicEmbed.success(
            title="**I'm already in a voice channel.**",
            description=f"👉 {ctx.voice_client.channel}",
        )

        await ctx.reply(
            embed=embed,
            mention_author=False,
        )

    async def message_connected(self, ctx: commands.Context, vc: wavelink.Player):
        embed = MusicEmbed.success(
            action="Joined the voice channel",
            author=ctx.author,
            title=f"🔊 **Connected to {vc.channel}**",
        )

        await ctx.reply(
            embed=embed,
            mention_author=False,
        )

    async def message_disconnected(self, ctx: commands.Context, channel_name: str):
        embed = MusicEmbed.success(
            action="Left the voice channel",
            author=ctx.author,
            title=f"**Disconnected from {channel_name}**",
        )
        await ctx.reply(embed=embed, mention_author=False)

    async def message_play_single(
        self, ctx: commands.Context, vc: wavelink.Player, track: wavelink.Track
    ):
        embed = MusicEmbed.success(
            author=ctx.author,
            action="Play song",
            title=f"<:Reply:1076905179619807242>`{track.title}`",
            url=track.uri,
            description=f"Added by: {ctx.author.mention} | Duration: `{utils.get_time(track.length)}` | Position: `{len(vc.queue)}`",
        )

        await ctx.reply(
            embed=embed,
            mention_author=False,
        )

    async def message_play_multiple(
        self, ctx: commands.Context, vc: wavelink.Player, tracks: list[wavelink.Track]
    ):
        embed = MusicEmbed.success(
            ctx.author,
            action=f"Play list of songs",
            title=f"<:Reply:1076905179619807242>`Added {len(tracks)} songs to queue`",
            url=tracks[0].uri,
            description=f"Added by: {ctx.author.mention} | Duration: `{utils.get_lenght(tracks)}` | Queue lenght: `{len(vc.queue)}`",
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_queue_is_empty(self, ctx: commands.Context):
        embed = MusicEmbed.warning(
            ctx.author,
            "Queue is empty",
            description="Use `play` command to add songs.\n**or**\nUse `np` command to show current song.",
        )

        await ctx.reply(
            embed=embed,
            mention_author=False,
        )

    async def message_queue_cleared(self, ctx: commands.Context):
        await ctx.reply(
            embed=MusicEmbed.success(
                ctx.author, "Queue cleared", description="Queue is empty now."
            ),
            mention_author=False,
        )

    def _track_fragment(self, track: wavelink.Track, index: int):
        return (
            f"`{index + 1}.` [{track.title}]({track.uri}) `{utils.get_time(track.duration)}`\n"
            + f"<:Reply:1076905179619807242> **Author**: {track.author}"
        )

    async def message_queue(
        self,
        ctx: commands.Context,
        current: wavelink.Track,
        queue: wavelink.WaitQueue,
        pos: int,
    ):
        desc = "\n".join(
            [
                self._track_fragment(track, index)
                for index, track in enumerate(queue)
                if pos <= index and index < pos + 10
            ]
        )
        embed = MusicEmbed.success(
            ctx.author,
            "Queue display",
            title=f"**Current queue lenght**: `{len(queue)}`",
            description=desc,
        )
        embed.add_field(
            name="**Now playing**:",
            value=f"[{current.title}]({current.uri}) `{utils.get_time(current.duration)}`\n"
            + f"<:Reply:1076905179619807242>**Author**: {current.author}",
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_skipped(self, ctx: commands.Context, track: wavelink.Track):
        embed = MusicEmbed.success(
            ctx.author,
            "Skipped current song",
            title=f"<:Reply:1076905179619807242> `{track.title}`",
            url=track.uri,
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_skipped_next(
        self, ctx: commands.Context, prev: wavelink.Track, next: wavelink.Track
    ):
        embed = MusicEmbed.success(
            ctx.author,
            aciton="Skipped track, now playing:",
            title=f"<:Reply:1076905179619807242> `{next.title}`",
            url=next.uri
        )
        embed.add_field(value=f"**Previous**:", value=f"<:Reply:1076905179619807242> [{prev.title}]({prev.uri})")

        await ctx.reply(embed=embed, mention_author=False)

    async def message_skip_all(self, ctx: commands.Context, queue: WaitQueue):
        embed = MusicEmbed.success(
            ctx.author,
            action="Skipped all songs",
            title=f"<:Reply:1076905179619807242> Skipped: `{len(queue)}` tracks"
        )
        await ctx.reply(embed=embed, mention_author=False)

    async def message_no_track(self, ctx):
        embed = MusicEmbed.warning(
            ctx.author,
            title="No track currenlty",
            description="Use `play` command to add songs.\n**or**\nUse `np` command to show current song.",
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_now_playing(self, ctx: commands.Context, vc: wavelink.Player):
        embed = MusicEmbed.success(
            ctx.author,
            action="Now playing:",
            title=f"<:Reply:1076905179619807242> {vc.track} `{utils.get_time(vc.track.duration)}`",
        )

        await ctx.reply(embed=embed, mention_author=False)
    
    async def message_volume(self, ctx: commands.Context, vol):
        embed = MusicEmbed.success(
            ctx.author,
            action="Volume",
            title=f"Volume set to `{vol}`"
        )

        await ctx.reply(embed=embed, mention_author=False) 

    async def message_volume_current(self, ctx: commands.Context, vc: wavelink.Player):
        embed = MusicEmbed.success(
            ctx.author,
            action="Volume",
            title=f"Current volume is `{vol}`"
        )

        await ctx.reply(embed=embed, mention_author=False) 

    async def message_seek(self, ctx: commands.Context, prev: str, next: str, track: wavelink.Track):
        embed = MusicEmbed.success(
            ctx.author,
            action="Seeked time",
            title=f"`{prev}` -> `{next}`",
            description=f"[{track.title}]({track.uri}) `{utils.get_time(track.duration)}`\n"
            + f"<:Reply:1076905179619807242> **Author**: {track.author}"
        )
        await ctx.reply(embed=embed, mention_author=False)

    async def message_filter_list(self, ctx: commands.Context, filters: list[str]):
        ...