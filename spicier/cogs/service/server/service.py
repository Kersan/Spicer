from discord.ext import commands


class ServerService:
    """Service for server commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # TODO: Embed messeges for prefix group commands
