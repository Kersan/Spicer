from discord.ext import commands, tasks
from utils import request


# Usunięcie wiadomości
class Twitch(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = bot.config

        # Link do kanału/live twitch
        self.twitch_url = "https://www.twitch.tv/"

        # Lista streamerów, którzy mają live
        self.liveON = []

        self.print_cos.start()

    @tasks.loop(seconds=120)
    async def print_cos(self):
        await self.bot.wait_until_ready()

        for key, value in self.config.twitch.items():
            data = await request.get_html(self.twitch_url + value)

            if self.is_live(data):
                if value in self.liveON:
                    continue

                self.liveON.append(value)
                print(f"{key} właśnie odpalił live!")

                for channel_id in self.config.modules_twitch:
                    channel = self.bot.get_channel(channel_id)

                    await channel.send(f"{key} jest LIVE!")

            elif value in self.liveON:
                self.liveON.remove(value)

    @staticmethod
    def is_live(data):
        return '''"isLiveBroadcast":true''' in data
