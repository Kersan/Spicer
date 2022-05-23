from discord.ext import commands, tasks


# Usunięcie wiadomości
class Twitch(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.print_cos.start()

    @tasks.loop(seconds=120)
    async def print_cos(self):
        await self.bot.wait_until_ready()

        print("siema")
