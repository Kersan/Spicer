import asyncio
import json
import os

from spicier import SpicerBot


def get_token():
    with open("config/default.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        return config["token"]


if not os.path.exists("config/default.json"):
    configExample = ""
    with open("config/default-example.json", "r", encoding="utf-8") as example:
        configExample = example.read()

    with open("config/default.json", "w", encoding="utf-8") as config:
        config.write(configExample)

if not os.path.exists("logs"):
    os.mkdir("logs")


if not "BOT_TOKEN" in os.environ:
    configToken = get_token()

    if not configToken or len(configToken) < 16:
        raise RuntimeError(
            "Token not set in environment variables and is not valid in config.json!\n"
            "Please set the token in env or use a valid token in config.json"
        )

    # should add to env, but not working 😜
    os.environ["BOT_TOKEN"] = configToken


async def main():
    bot = SpicerBot()
    await bot.run(os.environ.get("BOT_TOKEN", get_token()))


if __name__ == "__main__":
    # 🚀 Launch the bot
    asyncio.run(main())
