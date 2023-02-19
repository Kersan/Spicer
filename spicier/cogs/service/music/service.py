import wavelink
from discord.ext import commands
from wavelink.errors import NodeOccupied

from .handler import MusicHandlers


class MusicService(MusicHandlers):
    def __init__(self, bot, filters):
        self.bot = bot
        self.filters = filters

        super().__init__(filters)

    async def create_nodes(self, config):
        try:
            await self.bot.wait_until_ready()
            await wavelink.NodePool.create_node(bot=self.bot, **config)
        except NodeOccupied:
            pass

    def is_alone(self, ctx: commands.Context) -> bool:
        return len(ctx.voice_client.channel.members) == 1
