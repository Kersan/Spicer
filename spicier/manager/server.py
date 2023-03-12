from spicier.cache import Cache
from spicier.config import Config
from spicier.database import Database
from spicier.models import Server


class ServerManager:
    """Hadles all server related operations"""

    def __init__(self, cache: Cache, db: Database, config: Config):
        self._config = config
        self._cache = cache
        self._db = db

    async def get(self, server_id: int) -> Server:
        """Get the server for the given ID"""
        cached = self._cache.get_server(server_id)
        if cached:
            return cached

        result = await self._db.server.get(server_id)

        server = None
        if not result:
            server = await self.create(server_id)
        else:
            server = Server.create(result)

        await self.set_cache(server_id, server)

        return server

    async def set_cache(self, server_id: int, server: Server):
        """Set the cache for the given server"""
        self._cache.set_server(server_id, server)

    async def get_channel(self, server_id: int) -> int:
        """Get the channel for the given server"""
        server = await self.get(server_id)
        return server.channel

    async def get_prefix(self, server_id: int) -> str:
        """Get the prefix for the given server"""
        server = await self.get(server_id)
        return server.prefix

    async def set_channel(self, server_id: int, channel: int):
        """Set the channel for the given server"""
        server = await self.get(server_id)
        server.channel = channel

        await self._db.server.set_channel(server_id, channel)
        await self.set_cache(server_id, server)

    async def set_prefix(self, server_id: int, prefix: str):
        """Set the prefix for the given server"""
        server = await self.get(server_id)
        server.prefix = prefix

        await self._db.server.set_prefix(server_id, prefix)
        await self.set_cache(server_id, server)

    async def clear_channel(self, server_id: int):
        """Clear the channel for the given server"""
        server = await self.get(server_id)
        server.channel = None

        await self._db.server.clear_channel(server_id)
        await self.set_cache(server_id, server)

    async def create(self, server_id: int) -> Server:
        """Create a new server empty server with the given ID"""
        await self._db.server.create(server_id)
        return Server(server_id)
