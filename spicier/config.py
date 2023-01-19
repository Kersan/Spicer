import json


class BadConfig(Exception):
    def __init__(self, cause: Exception):
        self.cause = cause


class Config:
    def __init__(self, path: str = "config/default.json"):
        self.path = path
        self.raw: json = self.__get_config()

    def __get_config(self):
        with open(self.path, "r", encoding="utf-8") as file:
            json_cfg = file
            return json.load(json_cfg)

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
