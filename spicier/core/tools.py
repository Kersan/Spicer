import logging
import os
from datetime import date
from os import path

from discord import Intents
from discord.ext import commands


async def load_cogs(bot: commands.Bot, cogs_dir: str = "spicier/cogs") -> None:
    """Load all cogs from the given directory"""
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            await bot.load_extension(f"spicier.cogs.{filename[:-3]}")
    logging.info(f"Loaded {len(bot.extensions)} cogs!")


def set_intents(intents: Intents = Intents.default()) -> Intents:
    """Setup intents for the bot"""
    intents.message_content = True
    intents.members = True
    intents.guilds = True

    return intents


def set_logging(
    logs_file: bool = True,
    file_level: int = logging.DEBUG,
    console_level: int = logging.INFO,
) -> tuple[logging.Logger, logging.StreamHandler]:
    """Setup logging for the bot"""

    file_path = path.join("logs", "latest.log")

    logger = logging.getLogger("discord")
    logger_root = logging.getLogger("root")

    logger.setLevel(logging.INFO)

    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)

    log_formatter = logging.Formatter(
        fmt="[{asctime}] [{levelname:<8}] {name}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

    # Change the name of the file if it already exists
    if path.exists(file_path):
        _format_file(file_path)

    if logs_file:
        file_handler = _setup_file_handler(file_path, log_formatter, file_level)
        logger.addHandler(file_handler)
        logger_root.addHandler(file_handler)

        assert path.exists(file_path)

    console_handler = _setup_console_handler(logging, log_formatter, console_level)
    logger.addHandler(console_handler)

    return logger, console_handler


def _setup_file_handler(file_path, log_formatter, file_level) -> logging.FileHandler:
    """Creates a file handler for the logger"""
    handler = logging.FileHandler(filename=file_path, encoding="utf-8", mode="w")
    handler.setFormatter(log_formatter)
    handler.setLevel(file_level)

    return handler


def _setup_console_handler(
    logging, log_formatter, console_level
) -> logging.StreamHandler:
    """Creates a console handler for the logger"""
    handler = logging.StreamHandler()
    handler.setFormatter(log_formatter)
    handler.setLevel(console_level)

    return handler


def _format_file(file_path):
    """Change the name of the file if it already exists"""
    now = str(date.today())[2:]
    count = 0

    for _, __, files in os.walk("logs"):
        for file in files:
            if now in str(file):
                count += 1

    os.rename(file_path, f"logs/{str(date.today())[2:]}-{count}.log")
