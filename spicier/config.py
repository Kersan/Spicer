import json
import os

from .errors import BadConfig


class Config:
    """The config class"""

    def __init__(self, path: str = "config/default.json"):
        self._path = path
        self.raw: json = self._get_config()

        self.langs = {}
        self.update_langs()

        self._db_url = "postgresql://{}:{}@{}:{}/{}"

    def _get_config(self):
        with open(self._path, "r", encoding="utf-8") as file:
            json_cfg = file
            return json.load(json_cfg)

    def _get_lang_names(self):
        files = os.listdir("config/lang/")
        return {file[:-5]: file for file in files if file.endswith(".json")}

    def _get_lang(self, lang):
        with open(f"config/lang/{lang}.json", "r", encoding="utf-8") as file:
            json_lang = file
            return json.load(json_lang)

    def update_langs(self):
        """Update the langs dict"""
        self.langs = {lang: self._get_lang(lang) for lang in self._get_lang_names()}

    def prop(self, prop: str):
        """Get a property from the config"""
        try:
            return self.raw[prop]
        except Exception as exception:
            raise BadConfig(exception) from exception

    @property
    def database(self) -> str:
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL")
        
        db = self.prop("postgres")

        return self._db_url.format(
            db["user"], db["password"], db["host"], db["port"], db["database"]
        )

    @property
    def lavalink(self) -> dict:
        prop = self.prop("lavalink")

        if not os.getenv("LAVALINK_HOST"):
            return prop

        prop["host"] = os.getenv("LAVALINK_HOST")
        prop["port"] = os.getenv("LAVALINK_PORT")

        return prop

    @property
    def prefix(self) -> str:
        return self.prop("prefix")

    @property
    def delete_after(self) -> bool:
        return self.prop("delete_after")

    @property
    def delete_time(self) -> int:
        return self.prop("delete_time")

    @property
    def leave_time(self) -> int:
        return self.prop("leave_time")

    def lang(self, language: str) -> str:
        self.update_langs()
        return self.langs[language] or self.langs["en"]
