import logging
import time

import wavelink
from discord import Embed, TextChannel
from discord.ext import commands
from wavelink.errors import NodeOccupied
from wavelink.queue import WaitQueue

from spicier.embeds import MusicEmbed

from . import CustomFilters, utils
from .handler import MusicHandler


class MusicService:
    """Service for music commands"""

    def __init__(self, bot, filters: CustomFilters, logger: logging.Logger):
        self.bot = bot
        self.filters = filters
        self.handler = MusicHandler(filters, logger)

    async def create_nodes(self, config):
        await self.bot.wait_until_ready()
        try:
            await wavelink.NodePool.create_node(bot=self.bot, **config)
            return True
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

        await ctx.reply(embed=embed, mention_author=False)

    async def message_connected(self, ctx: commands.Context, vc: wavelink.Player):
        embed = MusicEmbed.success(
            action="Joined the voice channel",
            author=ctx.author,
            title=f"🔊 **Connected to {vc.channel}**",
        )

        await ctx.reply(embed=embed, mention_author=False)

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
            ctx.author,
            f"{ctx.guild.name} | Added to queue",
            title=f"`{track.title}`",
            url=track.uri,
            description=f"Added by: {ctx.author.mention} | Duration: `{utils.get_time(track.length)}` | Position: `{len(vc.queue)}`",
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_play_multiple(
        self, ctx: commands.Context, vc: wavelink.Player, tracks: list[wavelink.Track]
    ):
        embed = MusicEmbed.success(
            ctx.author,
            f"{ctx.guild.name} | Added to queue",
            title=f"Playlist of **{len(tracks)}** tracks",
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

        await ctx.reply(embed=embed, mention_author=False)

    async def message_queue_cleared(self, ctx: commands.Context):
        embed = MusicEmbed.success(
            ctx.author, "Queue cleared", description="Queue is empty now."
        )

        await ctx.reply(embed=embed, mention_author=False)

    def _track_fragment(self, track: wavelink.Track, index: int):
        return (
            f"`{index + 1}.` [{track.title}]({track.uri}) `{utils.get_time(track.duration)}`\n"
            + f"<:Reply:1076905179619807242> **Author**: {track.author}"
        )

    def _get_tracks(self, queue: WaitQueue, pos: int):
        trakcs = []
        for index, track in enumerate(queue):
            if pos <= index and index < pos + 8:
                trakcs.append(self._track_fragment(track, index))
        return trakcs

    async def message_queue(
        self,
        ctx: commands.Context,
        current: wavelink.Track,
        queue: wavelink.WaitQueue,
        pos: int,
        file=None,
    ):
        desc = "\n".join(self._get_tracks(queue, pos))
        embed = MusicEmbed.success(
            ctx.author,
            f"{ctx.guild.name} | Queue display",
            title=f"**{len(queue)}** songs in queue",
            description=desc,
        )
        embed.add_field(
            name="**Now playing**:",
            value=f"[{current.title}]({current.uri}) `{utils.get_time(current.duration)}`\n"
            + f"<:Reply:1076905179619807242>**Author**: {current.author}",
        )

        if file:
            embed.set_image(url=f"attachment://{file.filename}")

        await ctx.reply(embed=embed, mention_author=False, file=file)

    async def message_skipped(self, ctx: commands.Context, track: wavelink.Track):
        embed = MusicEmbed.success(
            ctx.author,
            "Skipped current song",
            title=f"`{track.title}`",
            url=track.uri,
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_skipped_next(
        self, ctx: commands.Context, prev: wavelink.Track, next: wavelink.Track
    ):
        vc: wavelink.Player = await utils.get_player(ctx)

        embed = MusicEmbed.success(
            ctx.author,
            f"{ctx.guild.name} | Skipped, now playing",
            title=f"`{next.title}`",
            url=next.uri,
            description=f"Skipped by: {ctx.author.mention} | Duration: `{utils.get_time(next.length)}` | Queue: `{len(vc.queue)}`",
        )
        embed.add_field(
            name=f"**Previous**:",
            value=f"<:Reply:1076905179619807242> [{prev.title}]({prev.uri})",
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_skip_all(self, ctx: commands.Context, queue: WaitQueue):
        embed = MusicEmbed.success(
            ctx.author,
            action="Skipped all songs",
            title=f"<:Reply:1076905179619807242> Skipped: `{len(queue)}` tracks",
        )
        await ctx.reply(embed=embed, mention_author=False)

    async def message_no_track(self, ctx):
        embed = MusicEmbed.warning(
            ctx.author,
            title="No track currenlty",
            description="Use `play` command to add songs.\n**or**\nUse `np` command to show current song.",
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_now_playing(
        self, ctx: commands.Context, vc: wavelink.Player, image=None
    ):
        embed = MusicEmbed.success(
            author=ctx.author,
            action=f"{ctx.guild.name} | Now playing",
            title=f"`{vc.track.title}`",
            url=vc.track.uri,
        )

        embed.add_field(name="**Current Volume**:", value=f"`{vc.volume}`")
        embed.add_field(name="**Track's Author**:", value=f"`{vc.track.author}`")
        embed.add_field(
            name="**Track's Source**:",
            value=f"`{vc.track.info['sourceName'] or 'Unknown'}`",
        )
        embed.add_field(
            name="**Position**:",
            value=f"**`{utils.get_time(vc.position)}`**/`{utils.get_time(vc.track.duration)}`",
        )

        if image:
            embed.set_image(url=f"attachment://{image.filename}")

        await ctx.reply(embed=embed, mention_author=False, file=image)

    async def message_volume(self, ctx: commands.Context, vol):
        embed = MusicEmbed.success(
            ctx.author, action="Volume", title=f"Volume set to `{vol}`"
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_volume_current(self, ctx: commands.Context, vol: int):
        embed = MusicEmbed.success(
            ctx.author, action="Volume", title=f"Current volume is `{vol}`"
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_seek(
        self, ctx: commands.Context, prev: int, next: int, vc: wavelink.Player
    ):
        track: wavelink.Track = vc.track

        embed = MusicEmbed.success(
            ctx.author,
            action=f"{ctx.guild.name} | Seeked time",
            title=f"`{track.title}`",
            description=f"Track's duration: `{utils.get_time(track.duration)}`",
            url=track.uri,
        )
        embed.add_field(
            name="Seeked from - to:",
            value=f"`{utils.get_time(prev)}` - `{utils.get_time(next)}`",
        )

        image = utils.get_proggres_bar(next, track.duration)
        embed.set_image(url=f"attachment://{image.filename}")

        await ctx.reply(embed=embed, mention_author=False, file=image)

    def _add_filter(self, embed: Embed, name: str, filter):
        embed.add_field(name=f"`{name}`", value=filter.description, inline=True)
        return embed

    async def message_filter_list(self, ctx: commands.Context):
        embed = MusicEmbed.success(
            ctx.author, action="Filters", title=f"Avaliable filters: "
        )
        for name, filter in self.filters.modes.items():
            embed = self._add_filter(embed, name, filter)

        await ctx.reply(embed=embed, mention_author=False)

    async def message_filter_set(self, ctx: commands.Context, mode: str):
        embed = MusicEmbed.success(
            ctx.author, action="Filters", title=f"Filter set to `{mode}`"
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_filter_clear(self, ctx: commands.Context):
        embed = MusicEmbed.success(ctx.author, title=f"Filters cleared")

        await ctx.reply(embed=embed, mention_author=False)

    async def message_filter_current(
        self, ctx: commands.Context, filter: str, desc: str
    ):
        embed = MusicEmbed.success(
            ctx.author,
            "Filters",
            title=filter,
            description=f"<:Reply:1076905179619807242> {desc}",
        )

        await ctx.reply(embed=embed, mention_author=False)

    async def message_queue_empty(self, channel: TextChannel):
        embed = MusicEmbed.warning(
            channel.guild.me,
            f"{channel.guild.name} | Queue",
            title="Queue is empty",
            description="Use `play` command to add songs.",
        )

        await channel.send(embed=embed)

    async def message_next_track(
        self, channel: TextChannel, vc: wavelink.Player, track: wavelink.Track
    ):
        embed = MusicEmbed.success(
            channel.guild.me,
            f"{channel.guild.name} | Now playing",
            title=f"`{track.title}`",
            url=track.uri,
        )

        embed.add_field(name="**Duration**:", value=f"`{utils.get_time(track.length)}`")
        embed.add_field(name="**Track's Author**:", value=f"`{track.author}`")
        embed.add_field(
            name="**Track's Source**:",
            value=f"`{track.info['sourceName'] or 'Unknown'}`",
        )

        await channel.send(embed=embed)
