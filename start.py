from bot import Bot
from configparser import ConfigParser

config = ConfigParser()

cfg = config.read("config.ini", encoding="utf-8")
token = config.get(section="BOT", option="TOKEN")

if __name__ == "__main__":

    bot = Bot(token, cfg)
    bot.run()
