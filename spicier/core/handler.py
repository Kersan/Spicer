import logging
from typing import Union

from discord import Message
from discord.ext import commands
from discord.ext.commands import errors as commands_errors

from spicier.errors import (
    PlayerNotPlaying,
    QueueEmpty,
    VoiceConnectionError,
    WrongArgument,
)

core_logger = logging.getLogger("spicier.core")


class EventHandler(commands.Cog):
    """Handles bot events"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.delete = bot.config.delete_after
        self.delete_time = bot.config.delete_time

    @commands.Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if before.content != after.content:
            await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        ...

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

    async def handle_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> Union[bool, None]:
        """Handle errors and return True if error should be raised"""
        if isinstance(error, commands_errors.MissingPermissions):
            pass

        elif isinstance(error, commands_errors.CheckFailure):
            pass

        elif isinstance(error, commands_errors.MissingRequiredArgument):
            await self.send_error(
                ctx, f"Missing required argument: `{error.param.name}`", error
            )

        elif isinstance(error, commands_errors.CommandNotFound):
            await self.send_error(
                ctx, f"Command not found: `{ctx.message.content}`", error
            )

        elif isinstance(error, commands_errors.ChannelNotFound):
            await self.send_error(ctx, f"Channel not found: `{error.argument}`", error)

        elif isinstance(error, VoiceConnectionError):
            msg = (
                "Something went wrong with the voice connection"
                if not error.message
                else error.message
            )
            await self.send_error(ctx, msg, error)

        elif isinstance(error, QueueEmpty):
            await self.send_error(ctx, "The queue is empty", error, debug=False)

        elif isinstance(error, WrongArgument):
            await self.send_error(
                ctx, f"Unvalid argument: `{error.message}`", error, debug=False
            )

        elif isinstance(error, PlayerNotPlaying):
            await self.send_error(
                ctx, "Before using this command, play something", error, debug=False
            )

        else:
            core_logger.error(str(error))
            return True

    async def send_error(
        self,
        ctx: commands.Context,
        message: str,
        error: commands.CommandError,
        debug=True,
    ):
        """Reply with error message and log error"""
        await ctx.reply(message, delete_after=self.delete_time)
        if debug:
            core_logger.debug(str(error))
