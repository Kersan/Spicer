import logging

from discord import errors
from discord.ext import commands


class ErrorHandler(commands.Cog):
    """Handles bot errors"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, errors.MissingPermissions):
            return

        if self.config.delete_after:
            await ctx.message.delete(delay=self.config.delete_time)

        if isinstance(error, errors.WrongArgument):
            await ctx.reply(
                error.message + f"\n```{error.cause}```",
                delete_after=self.config.delete_time,
            )
            logging.debug(str(error))

        if isinstance(error, errors.ArgumentNeeded):
            await ctx.reply(
                f"Required arguments not found: `{error.needed}` \nInstead passed: `{error.arguments}`!",
                delete_after=self.config.delete_time,
            )
            logging.debug(str(error))

        else:
            if ctx.message.author.guild_permissions.administrator:
                await ctx.reply(
                    f"Coś poszło nie tak: ```{error}```",
                    delete_after=self.config.delete_time,
                )

            logging.debug(str(error))
