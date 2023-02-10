from os import path

import pytest
from asyncpg import Pool

from spicier.config import Config
from spicier.database import Database

pytest_plugins = ("pytest_asyncio",)

cfg_path = "config/default.json"

if not path.exists(cfg_path):
    cfg_path = "config/default.json"


@pytest.mark.asyncio
async def test_primary():
    database = Database(**Config(path=cfg_path).database)
    await database.start()
    assert database.pool is not None


@pytest.mark.asyncio
async def test_setup():
    database = Database(**Config(path=cfg_path).database)
    await database.start()
    await database.setup()
    assert database.pool is not None


@pytest.mark.asyncio
async def test_tables():
    database = Database(**Config(path=cfg_path).database)
    await database.start()

    pool: Pool = database.pool

    assert isinstance(pool, Pool)

    tables = await pool.fetchval("SELECT * FROM pg_catalog.pg_tables;")
    await pool.close()

    assert len(tables) > 0
