import logging
import os
import time
from dataclasses import dataclass

import asyncpg
from asyncpg import Pool

from .tables import PlaylistTable, QueueTable, ServerTable, SkipTable

database_logger = logging.getLogger("spicier.database")


@dataclass
class DBData:
    user: str
    password: str
    database: str
    host: str
    port: int


class Database(DBData):
    """Database class for interacting with the database"""

    server: ServerTable
    skip: SkipTable
    queue: QueueTable
    playlist: PlaylistTable

    def __init__(self, **kwargs):
        super(Database, self).__init__(**kwargs)
        self.pool: Pool = None

    @property
    def settings(self) -> dict:
        """Return the database settings"""
        return {
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "host": self.host,
            "port": self.port,
        }

    async def start(self):
        """Start the database connection.
        Try to connect to the database 5 times with a 5 second delay between each attempt.
        """
        tries = 5
        fail_msg = "Failed to connect to database. Retrying... ({}/{})"

        for i in range(tries):
            if await self._try_connect():
                break
            else:
                database_logger.warning(fail_msg.format(i + 1, tries))
                time.sleep(5)

        if self.pool:
            database_logger.info("Connected to database")

    async def setup(self, path: str = "spicier/database/sql"):
        """Setup database with sql scripts"""
        sqls = self._get_scripts(path)

        database_logger.info(f"Setting up database with {len(sqls)} scripts...")

        for sql in sqls:
            await self._execute_file(path, sql)

        self._build_tables()

        database_logger.info("Database setup complete")

    def _get_scripts(self, path: str) -> list:
        sqls = [file for file in os.listdir(path) if file.endswith(".sql")]

        if len(sqls) == 0:
            database_logger.warning("No sql scripts found in given path")
            return []

        return sqls

    async def _execute_file(self, path: str, sql: str):
        with open(f"{path}/{sql}", "r") as file:
            return await self.pool.execute(file.read())

    async def _try_connect(self) -> bool:
        try:
            self.pool = await asyncpg.create_pool(**self.settings)
            return True
        except Exception as exception:
            database_logger.error(f"Failed to connect to database: {exception}")
            return False

    def _build_tables(self):
        database_logger.info("Creating managers for database tables...")

        self.server = ServerTable(self.pool, "server")
        self.skip = SkipTable(self.pool, "skip")
        self.queue = QueueTable(self.pool, "queue")
        self.playlist = PlaylistTable(self.pool, "playlist")
