import asyncpg


class Table:
    def __init__(self, pool: asyncpg.Pool, name: str = ""):
        self.pool = pool
        self.name = name


class SkipTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ServerTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def clearMusicParams(self, guild_id: int, is_playing: bool, is_paused: bool):
        self.pool.execute(
            "UPDATE server SET is_playing = $1, is_paused = $2 WHERE guild_id = $3",
            is_playing,
            is_paused,
            guild_id,
        )


class QueueTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def add(
        self,
        guild_id: int,
        is_playing: bool,
        requester: str,
        channel_id: int,
        uri: str,
        title: str,
        duration: int,
        index: int,
    ):
        self.pool.execute(
            "INSERT INTO queue VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
            guild_id,
            is_playing,
            requester,
            channel_id,
            uri,
            title,
            duration,
            index,
        )

    async def clear(self, guild_id: int):
        await self.pool.execute(f"DELETE FROM queue WHERE guild_id = $1", guild_id)

    async def countQueueItems(self, guild_id: int):
        result = await self.pool.fetchval(
            "SELECT COUNT(*) FROM queue WHERE guild_id = $1 AND index != 0", guild_id
        )
        print(result)
        return result[0]

    async def getFutureIndex(self, guild_id: int):
        result = await self.pool.fetchval(
            "SELECT MAX(index) FROM queue WHERE guild_id = $1", guild_id
        )
        print(result)
        return result[0]

    async def queueSizeAndDuration(self, guild_id: int):
        result = await self.pool.fetchval(
            "SELECT SUM(duration), COUNT(*) FROM queue WHERE guild_id = $1 AND isPlaying = False AND index != 0",
            guild_id,
        )
        print(result)
        return result[0]


class PlaylistTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
