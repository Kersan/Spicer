import asyncio

import discord
from discord.ext import commands
from .mongo.db import Mongo

from bot.cogs import COGS


class Bot(commands.Bot):
    def __init__(self, token: str, config):

        self.config = config
        self.TOKEN = token

        intents = self.get_intents(discord.Intents.default())

        super().__init__(
            command_prefix=self.prefix,
            case_insensitive=True,
            intents=intents
        )

        self.Mongo = Mongo("mongodb://localhost:27017")

    def run(self):
        super().run(self.TOKEN, reconnect=True)

    async def prefix(self, bot, msg):
        return commands.when_mentioned_or("!")(bot, msg)

    """ EVENTY BOTA """

    async def on_ready(self):
        pass

    async def setup_hook(self) -> None:
        for cog in COGS:
            await self.add_cog(cog(self))

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

    @staticmethod
    def get_intents(intents):
        intents.message_content = True
        intents.members = True
        intents.guilds = True

        return intents
