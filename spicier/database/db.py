import logging
import os
from dataclasses import dataclass

import asyncpg
from asyncpg import Pool

from .tables import PlaylistTable, QueueTable, ServerTable, SkipTable


@dataclass
class DBData:
    user: str
    password: str
    database: str
    host: str
    port: int


class Database(DBData):
    def __init__(self, **kwargs):
        super(Database, self).__init__(**kwargs)
        self.pool: Pool = None

        self.skip = SkipTable(self.pool, "skip")
        self.server = ServerTable(self.pool, "server")
        self.queue = QueueTable(self.pool, "queue")
        self.playlist = PlaylistTable(self.pool, "playlist")

    async def start(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=self.user,
                password=self.password,
                database=self.database,
                host=self.host,
                port=self.port,
            )
        except Exception as e:
            logging.error(f"Error while connecting to database: {e}")

    async def setup(self, path: str = "spicier/database/sql"):
        """Setup the database by running all the sql scripts from the given path"""
        sqls = [file for file in os.listdir(path) if file.endswith(".sql")]

        if len(sqls) == 0:
            logging.warning("No sql scripts found in given path")
            return

        async def execute(sql):
            with open(f"{path}/{sql}", "r") as file:
                return await self.pool.execute(file.read())

        logging.info(f"Setting up database with {len(sqls)} scripts...")

        try:
            for sql in sqls:
                await execute(sql)
        except Exception as e:
            logging.error(f"Error while setting up database: {e}")

        logging.info("Database setup complete")
