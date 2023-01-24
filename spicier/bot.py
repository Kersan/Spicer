import logging
import os

import discord
from discord import utils
from discord.ext import commands

from .config import Config
from .core import ErrorHandler, tools
from .database import Database


class SpicerBot(commands.Bot):
    def __init__(self):
        self.handler = None
        self.logger = None
        self.config = Config()
        self.db = Database(**self.config.database)

        super().__init__(
            command_prefix=self.config.prefix,
            intents=tools.set_intents(),
            case_insensitive=True,
        )

    async def run(self, token):
        await self.setup_bot()

        await super().start(
            token,
            reconnect=True,
        )

    async def setup_hook(self):
        await self.setup_database()
        await self.setup_cogs()

    async def setup_database(self):
        await self.db.start()
        await self.db.setup()

        assert self.db.pool is not None, "Database was not initialized correctly!"

    async def setup_cogs(self):
        await self.add_cog(ErrorHandler(self))

        for filename in os.listdir("spicier/cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"spicier.cogs.{filename[:-3]}")
        logging.info(f"Loaded {len(self.extensions)} cogs!")

    async def setup_bot(self):
        self.logger, self.handler = tools.set_logging(logs_file=False)
        utils.setup_logging(handler=self.handler, level=logging.INFO)

    async def on_ready(self):
        channel = self.get_channel(890257740868485123)
        await channel.send("Bot is ready!")

    async def close(self):
        self.logger.info("Closing bot...")
        await super().close()

    async def on_message(self, msg):
        if msg.guild is None or msg.author.bot:
            return

        await self.process_commands(msg)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content != after.content:
            await self.process_commands(after)

    async def on_command_completion(self, ctx):
        if self.config.delete_after:
            await ctx.message.delete(delay=self.config.delete_time)
