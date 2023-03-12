import logging

from discord import Message
from discord.ext import commands

from spicier.manager import ServerManager
from spicier.models import Server

from .service import ErrorService

core_logger = logging.getLogger("spicier.core")


class EventHandler(commands.Cog, ErrorService):
    """Handles bot events"""

    server_manager: ServerManager

    def __init__(self, bot: commands.Bot) -> None:
        self.server_manager = bot.server_manager
        self.bot = bot

        super().__init__(bot, core_logger)

    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @commands.Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if before.content != after.content:
            await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        if "MusicCog" in ctx.command.cog_name:
            await self.handle_music_cog(ctx)

    async def handle_music_cog(self, ctx: commands.Context):
        channel: int = await self.server_manager.get_channel(ctx.guild.id)

        if channel and channel == ctx.channel.id:
            return

        await self.server_manager.set_channel(ctx.guild.id, ctx.channel.id)

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if self.delete:
            await ctx.message.delete(delay=self.delete_time)

        raise_error: bool = (  # If both are true, raise error
            await self.handle_error(ctx, error)
            and ctx.message.author.guild_permissions.administrator
        )

        if raise_error:
            raise error
