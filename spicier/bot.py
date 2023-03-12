import logging

from discord import utils
from discord.ext import commands

from .config import Config
from .core import EventHandler
from .core import tools as core
from .database import Database

bot_logger = logging.getLogger("spicier")


class Setup:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db

        self.cogs_dir = "spicier/cogs"

    async def start(self):
        await self.setup_database()
        await self.setup_cogs()

    async def setup_database(self):
        await self.db.start()

        try:
            await self.db.setup()
        except Exception as e:
            bot_logger.error(f"Error while setting up database: {e}")

        assert self.db.pool, "Database was not initialized correctly!"

    async def setup_cogs(self):
        await self.bot.add_cog(EventHandler(self.bot))
        await core.load_cogs(self.bot, cogs_dir=self.cogs_dir)


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

        await super().start(token, reconnect=True)

    async def setup_hook(self):
        await Setup(self).start()

    async def on_ready(self):
        pass

    async def close(self):
        self.logger.info("Closing bot...")
        await super().close()

    async def on_message(self, msg):
        if msg.author.bot:
            return

        if msg.guild:
            await self.process_commands(msg)
