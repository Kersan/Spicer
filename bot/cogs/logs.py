import discord
from discord.ext import commands
from utils import embed

# Usunięcie wiadomości
class MessageDelete(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = bot.config
        self.log_channels = list(bot.config.log_message.keys())

    def check(self, message: discord.Message):
        if message.author.bot:
            return False
        
        if message.guild.id not in self.config.modules_logs:
            return False

        return True

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        
        if not self.check(message):
            return

        self.bot.Mongo.message_deleted(
            guild_id=message.guild.id,
            user_id=message.author.id,
            before=message.content
        )

        if message.guild.id in self.log_channels:
            channel_id = self.config.log_message[message.guild.id]
            channel = self.bot.get_channel(channel_id)

            delete_embed = embed.create_embed(
                title="Wiadomość usunięta",
                user=message.author, 
                description=f"```{message.content}```",
                color=0xff0036,
                add_date=True
            )
            print(delete_embed)

            await channel.send(embed=delete_embed)

# Edytowanie wiadomości
class MessageEdit(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = bot.config
        self.log_channels = list(bot.config.log_message.keys())

    def check(self, message: discord.Message):
        if message.author.bot:
            return False
        
        if message.guild.id not in self.config.modules_logs:
            return False

        return True

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        
        if not self.check(before):
            return

        if before.content == after.content:
            return

        self.bot.Mongo.message_edited(
            guild_id=before.guild.id,
            user_id=before.author.id,
            before=before.content,
            after=after.content
        )

        if before.guild.id in self.log_channels:
            channel_id = self.config.log_message[before.guild.id]
            channel = self.bot.get_channel(channel_id)

            edited_embed1 = embed.create_embed(
                title="Wiadomość edytowana",
                user=before.author, 
                description=f"Przed:\n```{before.content}```",
                color=0x0053ff,
                add_date=False
            )

            edited_embed2 = embed.create_embed(
                title="",
                description=f"Po:\n```{after.content}```",
                color=0x7600ff,
                add_date=True
            )

            await channel.send(embed=edited_embed1)
            await channel.send(embed=edited_embed2)

