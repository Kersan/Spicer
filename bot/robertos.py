import asyncio
from re import T

import discord
from discord.ext import commands
from .mongo.db import Mongo
from utils.config import Config

from bot.cogs import *


class Bot(commands.Bot):
    def __init__(self, config_path):

        self.config = Config(config_path)
        self.Mongo = Mongo("mongodb://localhost:27017")

        ####################
        # DISCORD RZECZY 🥶

        intents = self.get_intents(discord.Intents.default())

        # Initializacja klasy commands.Bot
        super().__init__(
            command_prefix=self.prefix,
            case_insensitive=True,
            intents=intents
        )

    ##############
    # Robertos 😼

    def run(self):
        """ Metoda startowa bota 🚀 """
        super().run(self.config.token, reconnect=True)

    async def prefix(self, bot, msg):
        """ Zwraca możliwe prefixy """
        return commands.when_mentioned_or("!")(bot, msg)

    @staticmethod
    def get_intents(intents):
        """ Zwraca potrzebne do działania bota ustawienia intentsów """
        intents.message_content = True
        intents.members = True
        intents.guilds = True

        return intents

    ################
    # Eventy bota ⚙

    async def on_ready(self):
        pass

    async def setup_hook(self) -> None:
        cogs = TWICH_COGS + UTILS_COGS

        # Wczytywanie cogów z domyślnymi ustawieniami
        for cog in cogs:
            await self.add_cog(cog(self))

        # wczytywanie cogów z jakimiś ustawieniami
        for cog in LOG_COGS:
            await self.add_cog(cog(self), guilds=self.config.modules_logs)

    async def close(self):
        await super().close()

    async def on_connect(self):
        print("connected!")

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content != after.content:
            await self.process_commands(after)

    async def on_error(self, err, *args, **kwargs):
        raise
