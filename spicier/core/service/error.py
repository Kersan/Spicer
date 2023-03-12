import logging
from typing import Union

from discord.ext import commands
from discord.ext.commands import errors as commands_errors

from spicier.errors import (
    PlayerNotPlaying,
    QueueEmpty,
    VoiceConnectionError,
    WrongArgument,
)


class ErrorService:
    def __init__(self, bot: commands.Bot, logger: logging.Logger):
        self.delete_time = bot.config.delete_time
        self.delete = bot.config.delete_after
        self.bot = bot

        self.logger = logger

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
            self.logger.error(str(error))
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
            self.logger.debug(str(error))
