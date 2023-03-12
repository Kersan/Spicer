from typing import Union

from cachetools import TTLCache

from spicier.models import Server


class Cache:
    def __init__(self):
        self._servers = TTLCache(ttl=300, maxsize=1000)

    def get_server(self, server_id: int) -> Server:
        return self._servers.get(server_id)

    def set_server(self, server_id: int, server: Server):
        self._servers[server_id] = server

    def expire_server(self, server_id: int):
        del self._servers[server_id]
