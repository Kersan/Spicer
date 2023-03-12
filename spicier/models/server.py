from typing import Union


class Server:
    def __init__(
        self, server_id: Union[str, int], channel: int = None, prefix: str = None
    ):
        self.server_id = server_id
        self.channel = channel
        self.prefix = prefix

    def __eq__(self, other):
        return self.server_id == other.server_id

    @staticmethod
    def create(result):
        server = Server(result["id"])

        if result["channel"]:
            server.channel = result["channel"]

        if result["prefix"]:
            server.prefix = result["prefix"]

        return server
