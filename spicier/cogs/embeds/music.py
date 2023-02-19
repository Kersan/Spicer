from discord import Embed, User
from discord.ext import commands

DEFAULT_URL = "https://discord.gg/CKvaXz5"


class MusicEmbed:
    @staticmethod
    def success(
        author: User = None,
        action: str = None,
        title: str = None,
        description: str = None,
        url: str = None,
        thumbnail: str = None,
        color=0x2B2D31,
    ):
        embed = Embed(
            url=url,
            color=color,
            title=title,
            description=description,
        )
        embed.set_thumbnail(url=thumbnail)
        if author:
            embed.set_author(name=action, icon_url=author.avatar.url, url=DEFAULT_URL)

        return embed
