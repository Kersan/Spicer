import logging

from discord import utils
from discord.ext import commands

from .config import Config
from .core import EventHandler
from .core import tools as core
from .database import Database


class SpicerBot(commands.Bot):
    def __init__(self):
        self.handler = None
        self.logger = None
        self.config = Config()
        self.db = Database(**self.config.database)

        super().__init__(
            command_prefix=self.config.prefix,
            intents=core.set_intents(),
            case_insensitive=True,
        )

    async def run(self, token):
        self.logger, self.handler = core.set_logging(
            logs_file=False, console_level=logging.INFO
        )
        utils.setup_logging(handler=self.handler, level=logging.INFO)

        await super().start(
            token,
            reconnect=True,
        )

    async def setup_database(self):
        await self.db.start()
        await self.db.setup()

        assert self.db.pool is not None, "Database was not initialized correctly!"

    async def setup_cogs(self):
        await self.add_cog(EventHandler(self))
        await core.load_cogs(self, cogs_dir="spicier/cogs")

    async def setup_hook(self):
        await self.setup_database()
        await self.setup_cogs()

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
