import asyncpg


class Table:

    pool: asyncpg.Pool
    name: str

    def __init__(self, pool: asyncpg.Pool, name: str = ""):
        self.pool = pool
        self.name = name


class SkipTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ServerTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get(self, server_id: str):
        return await self.pool.fetchrow("SELECT * FROM server WHERE id = $1", server_id)

    async def create(self, server_id: int):
        await self.pool.execute("INSERT INTO server (id) VALUES ($1)", server_id)

    async def set_channel(self, server_id: int, channel: int):
        await self.pool.execute(
            "UPDATE server SET channel = $1 WHERE id = $2", channel, server_id
        )

    async def set_prefix(self, server_id: int, prefix: str):
        await self.pool.execute(
            "UPDATE server SET prefix = $1 WHERE id = $2", prefix, server_id
        )


class QueueTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PlaylistTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
