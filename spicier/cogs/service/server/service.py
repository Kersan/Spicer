from discord.ext import commands


class ServerService:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # TODO: Embed messeges for prefix group commands
