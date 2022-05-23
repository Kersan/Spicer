import os

from configparser import ConfigParser


class Config:
    def __init__(self, config_path):

        # Pobranie configu
        config = ConfigParser(interpolation=None)
        config.read(config_path, encoding="utf-8")

        # Sprawdzenie, czy wymagane sekcje znajdują się w configu
        confsections = {"BOT"}.difference(
            config.sections()
        )

        # Jeżeli którejś brakuje, to wyrzuca błąd
        if confsections:
            print(
                "Błąd podczas wczytywania configu!\n"
                "Nie udało się znaleźć poniższych sekcji:\n" +
                ", ".join(["[%s]" % s for s in confsections])
            )

        # BOT | TOKEN
        self.token = self.get_token(config.get("BOT", "TOKEN"))

    def get_token(self, cfg_token):
        if os.getenv("TOKEN"):
            return os.getenv("TOKEN")

        if len(cfg_token) < 70:
            return None

        return cfg_token
