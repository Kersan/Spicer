import os
import json
from configparser import ConfigParser
from utils.logger import Logging


class Config:
    """ Klasa pobierająca i przechowująca config """

    def __init__(self, config_path):

        # Pobranie configu
        config = ConfigParser(interpolation=None)
        config.read(config_path, encoding="utf-8")

        config_sections = {"BOT", "MODULES", "LOG_MESSAGE", "TWITCH"}

        # Sprawdzenie, czy wymagane sekcje znajdują się w configu
        confsections = config_sections.difference(
            config.sections()
        )

        # Jeżeli którejś brakuje, to wyrzuca błąd
        if confsections:
            raise Exception(
                "Błąd podczas wczytywania configu!\n"
                "Nie udało się znaleźć następujących sekcji: " +
                ", ".join(["[%s]" % s for s in confsections])
            )

        # Sprawdzenie, czy wszystkie opcje są uzupełnione 
        self.check_config(config, config_sections)


        default = DefaultConfig()

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

        # LOG_MESSAGE > dict
        self.log_message = self.__make_dict(config, "LOG_MESSAGE", default.log_message, use_int=True)

        # TWITCH > dict
        self.twitch = self.__make_dict(config, "TWITCH", default.twitch)

        Logging.info(__name__, "Config wczytany!")

    @staticmethod
    def __make_dict(cfg: ConfigParser, section: str, fallback: str, use_int: bool = False):
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

    def check_config(self, config: ConfigParser, sections):
        """ Metoda sprawdzająca sprawność configu """

        # Opcje bez przypisanej wartości:
        empty = []

        for section in sections:
            for option in config.options(section):
                
                # Jeżeli opcja nie ma wartości, dodaje do empty
                if not config.get(section, option):
                    empty.append(option)

        # Zawracam jak pusta lista
        if len(empty) == 0:
            return

        Logging.warning(__name__, "W configu znajdują się niewypełnione pola!")

        # TODO: Zrobić funckje, która będzie sprawdzała numer lini konkretnej opcji
        for i in empty:
            if i in config.options("BOT"):
                raise Exception(f"[CONFIG] Nie znaleziono kluczowej opcji {i}!")

            elif i in config.options("TWITCH"):
                raise Exception(f"[CONFIG] Nie podano nicku streamera dla opcji: {i}!")

            else:
                raise Exception(f"[CONFIG] Nie znaleziono wartości dla opcji {i}!")



class DefaultConfig:
    """ Domyślne ustawienia configu
    W tej klasie przechowuje domyślne wartości dla
    wymaganych kluczy z configu.
    """

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
