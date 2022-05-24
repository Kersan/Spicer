from discord.ext import commands


# Usunięcie wiadomości
class MessageDelete(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = bot.config
        self.log_channels = list(bot.config.log_message.keys())

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild.id not in self.config.modules_logs:
            return

        log_id = self.bot.Mongo.message_deleted(
            guild_id=message.guild.id,
            user_id=message.author.id,
            before=message.content
        )

        print(f"LOG-ID: {log_id}")

        if message.guild.id in self.log_channels:
            print("Wyśle tu wiadomość")


# Edytowanie wiadomości
class MessageEdit(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = bot.config
        self.log_channels = list(bot.config.log_message.keys())

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild.id not in self.config.modules_logs:
            return

        log_id = self.bot.Mongo.message_edited(
            guild_id=before.guild.id,
            user_id=before.author.id,
            before=before.content,
            after=after.content
        )

        print(f"LOG-ID: {log_id}")

        if before.guild.id in self.log_channels:
            print("Wyśle tu wiadomość")

