import json
import os


class BadConfig(Exception):
    def __init__(self, cause: Exception):
        self.cause = cause


class Config:
    def __init__(self, path: str = "config/default.json"):
        self.path = path
        self.raw: json = self._get_config()
        self.langs: dict = [self._get_lang(lang) for lang in self._get_lang_names()]

    def _get_config(self):
        with open(self.path, "r", encoding="utf-8") as file:
            json_cfg = file
            return json.load(json_cfg)

    def _get_lang_names(self):
        """Gets all json files names from /config/lang/ and returns them as a dict"""
        files = os.listdir("config/lang/")
        return {file[:-5]: file for file in files if file.endswith(".json")}

    def _get_lang(self, lang):
        with open(f"config/lang/{lang}.json", "r", encoding="utf-8") as file:
            json_lang = file
            return json.load(json_lang)

    def prop(self, prop: str):
        try:
            return self.raw[prop]
        except Exception as e:
            raise BadConfig(e)

    @property
    def database(self) -> dict:
        return self.prop("postgres")

    @property
    def prefix(self) -> str:
        return self.prop("prefix")

    @property
    def lavalink(self) -> dict:
        return self.prop("lavalink")

    @property
    def delete_after(self) -> bool:
        return self.prop("delete_after")

    @property
    def delete_time(self) -> int:
        return self.prop("delete_time")

    def lang(self, language: str) -> str:
        return self.langs.get(language, {})
