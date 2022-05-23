from discord.ext import commands


# Usunięcie wiadomości
class MessageDelete(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = bot.config

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        log_id = self.bot.Mongo.message_deleted(
            guild_id=message.guild.id,
            user_id=message.author.id,
            before=message.content
        )

        print(f"LOG-ID: {log_id}")


# Edytowanie wiadomości
class MessageEdit(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        log_id = self.bot.Mongo.message_edited(
            guild_id=before.guild.id,
            user_id=before.author.id,
            before=before.content,
            after=after.content
        )

        print(f"LOG-ID: {log_id}")
