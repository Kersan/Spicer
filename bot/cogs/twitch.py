from discord.ext import commands, tasks


# Usunięcie wiadomości
class Twitch(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.print_cos.start()

    @tasks.loop(seconds=3)
    async def print_cos(self):
        await self.bot.wait_until_ready()

        print("siema")

    # @commands.Cog.listener()
    # async def on_message_delete(self, message):
    #     log_id = self.bot.Mongo.message_deleted(
    #         guild_id=message.guild.id,
    #         user_id=message.author.id,
    #         before=message.content
    #     )
    #
    #     print(f"LOG-ID: {log_id}")
