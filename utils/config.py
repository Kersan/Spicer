import os
import json
from configparser import ConfigParser


class Config:
    def __init__(self, config_path):

        # Pobranie configu
        config = ConfigParser(interpolation=None)
        config.read(config_path, encoding="utf-8")

        # Domyślne ustawienia configu:
        default = DefaultConfig()

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
        self.token = self.__get_token(config.get(
            "BOT", "TOKEN", fallback=default.token)
        )
        # BOT | OWNER_IDS
        self.owner_ids = json.loads(config.get("BOT", "OWNER_IDS", fallback=default.owner_ids))
        # MODULES | LOGS
        self.modules_logs = json.loads(config.get("MODULES", "LOGS", fallback=default.modules_logs))
        # MODULES | TWICH
        self.modules_twitch = json.loads(config.get("MODULES", "TWITCH", fallback=default.modules_twitch))
        print(self.modules_twitch)
        # LOG_MESSAGE > dict
        self.log_message = self.make_dict(config, "LOG_MESSAGE", default.log_message, use_int=True)
        # TWITCH > dict
        self.twitch = self.make_dict(config, "TWITCH", default.twitch)

    @staticmethod
    def make_dict(cfg: ConfigParser, section: str, fallback: str, use_int: bool = False):
        options = cfg.options(section)
        if use_int:
            options = [int(x) for x in options]

        final = {}
        for option in options:
            if use_int:
                final[option] = cfg.getint(section, str(option), fallback=fallback)
            else:
                final[option] = cfg.get(section, option, fallback=fallback)

        return final

    @staticmethod
    def __get_token(cfg_token: str):
        if os.getenv("TOKEN"):
            return os.getenv("TOKEN")

        if len(cfg_token) < 70:
            return None

        return cfg_token


class DefaultConfig:
    def __init__(self):
        # BOT
        self.token = None
        self.owner_ids = None

        # MODULES
        self.modules_logs = None
        self.modules_twitch = None

        # LOGS
        self.log_message = None

        # TWICH
        self.twitch = None
