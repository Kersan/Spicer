from os import path

import pytest

pytest_plugins = ("pytest_asyncio",)

from spicier.config import Config
from spicier.database import Database

cfg_path = "config/default.json"

if not path.exists(cfg_path):
    cfg_path = "config/default.json"


def test_config():
    config = Config()
    assert config is not None
