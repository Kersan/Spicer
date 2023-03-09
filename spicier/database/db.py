import logging
import os
import time
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

    @property
    def settings(self) -> dict:
        return {
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "host": self.host,
            "port": self.port,
        }

    async def start(self):
        tries = 5
        fail_msg = "Failed to connect to database. Retrying... ({}/{})"

        for i in range(tries):
            if await self._try_connect():
                break
            else:
                logging.warning(fail_msg.format(i + 1, tries))
                time.sleep(5)

    async def setup(self, path: str = "spicier/database/sql"):
        """Setup database with sql scripts"""
        sqls = self._get_scripts(path)

        logging.info(f"Setting up database with {len(sqls)} scripts...")

        for sql in sqls:
            await self._execute(path, sql)

        logging.info("Database setup complete")

    def _get_scripts(self, path: str) -> list:
        sqls = [file for file in os.listdir(path) if file.endswith(".sql")]

        if len(sqls) == 0:
            logging.warning("No sql scripts found in given path")
            return []

        return sqls

    async def _execute(self, path: str, sql: str):
        with open(f"{path}/{sql}", "r") as file:
            return await self.pool.execute(file.read())

    async def _try_connect(self):
        try:
            self.pool = await asyncpg.create_pool(**self.settings)
        except Exception as e:
            logging.error(f"Failed to connect to database: {e}")
            return False
        else:
            return True
