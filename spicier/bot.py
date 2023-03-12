import logging

from discord import utils
from discord.ext import commands

from .cache import Cache
from .config import Config
from .core import EventHandler, tools
from .database import Database
from .manager import ServerManager


class Setup:
    @staticmethod
    async def database(bot: commands.Bot):
        database: Database = bot.db
        await database.start()

        try:
            await database.setup()
        except Exception as exception:
            raise exception

        assert database.pool, "Database was not initialized correctly!"

    @staticmethod
    async def events(bot: commands.Bot):
        await bot.add_cog(EventHandler(bot))

    @staticmethod
    async def managers(bot: commands.Bot):
        bot.server_manager = ServerManager(bot.cache, bot.db, bot.config)

    @staticmethod
    async def cogs(bot: commands.Bot):
        await bot.load_extension("spicier.cogs.music")
        await bot.load_extension("spicier.cogs.admin")


class SpicerBot(commands.Bot):

    config: Config
    cache: Cache
    db: Database

    COGS_DIR = "spicier/cogs"

    server_manager: ServerManager

    def __init__(self):
        self.handler = None
        self.logger = None

        self.config = Config()
        self.cache = Cache()

        self.db = Database(**self.config.database)

        super().__init__(**self.params)

    @property
    def params(self):
        return {
            "command_prefix": self.config.prefix,
            "intents": tools.set_intents(),
            "case_insensitive": True,
        }

    async def run(self, token):
        self.logger, self.handler = tools.set_logging(
            logs_file=False, console_level=logging.INFO
        )
        utils.setup_logging(handler=self.handler, level=logging.INFO)
        await super().start(token, reconnect=True)

    async def setup_hook(self):
        await Setup.database(self)
        await Setup.managers(self)
        await Setup.events(self)
        await Setup.cogs(self)

    async def close(self):
        self.logger.info("Closing bot...")
        await super().close()

    async def on_message(self, msg):
        if msg.author.bot:
            return

        if msg.guild:
            await self.process_commands(msg)
