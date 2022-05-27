from bot import Bot
from configparser import ConfigParser

# Wersja: 0.1.2 indev

# SCIEŻKA DO CONFIGU
CONFIG_PATH = "config.ini"


if __name__ == "__main__":

    config = ConfigParser()
    cfg = config.read(CONFIG_PATH, encoding="utf-8")

    bot = Bot(
        config_path=CONFIG_PATH
    )

    bot.run()

#########################################################
# TODO:
#  - Dodać klase, która będzie dziedziczyła z Exceptions
#    i dodać własne errory w miejsca ewentualnych błędów
#  - Logger
#  - Rozbudować logi wiadomości:
#    - Sprawdzenie, czy wiadomość ma pliki
#    - Sprawdzenie, czy długość wiadomości < 2000 - tworzyć plik
#    - Polepszyć te ochdne embedy 😉
#  - Twitch API może?
#  - Polimorfizm dla obu klas z cogs.logs - message
#
#  - Zmergować projekt z botem muzycznym czy coś 🥴... Może...?