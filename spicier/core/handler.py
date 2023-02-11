import logging

from discord import Message
from discord.ext import commands
from discord.ext.commands import errors as commands_errors


class EventHandler(commands.Cog):
    """Handles bot errors"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = bot.config

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands_errors.MissingPermissions):
            return

        if self.config.delete_after:
            await ctx.message.delete(delay=self.config.delete_time)

        if isinstance(error, commands_errors.MissingRequiredArgument):
            await ctx.reply(
                f"Required arguments not found: `{error.needed}` \nInstead passed: `{error.arguments}`!",
                delete_after=self.config.delete_time,
            )
            logging.debug(str(error))
            return

        if isinstance(error, commands_errors.CommandNotFound):
            await ctx.reply(
                f"Command not found: `{ctx.message.content}`",
                delete_after=self.config.delete_time,
            )
            logging.debug(str(error))
            return

        if isinstance(error, commands_errors.CheckFailure):
            return

        if ctx.message.author.guild_permissions.administrator:
            await ctx.reply(
                f"Coś poszło nie tak: ```{error}```",
                delete_after=self.config.delete_time,
            )

        logging.error(str(error))

    @commands.Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        if before.content != after.content:
            await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if self.config.delete_after:
            await ctx.message.delete(delay=self.config.delete_time)
