from discord import Embed, User

DEFAULT_URL = "https://discord.gg/CKvaXz5"


class MusicEmbed:
    """Embed builder for music commands"""

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
        """Build success embed"""
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

    @staticmethod
    def warning(
        author: User = None,
        action: str = None,
        title: str = None,
        description: str = None,
        color=0xFAA61A,
    ):
        """Build warning embed"""
        embed = Embed(
            color=color,
            title=title,
            description=description,
        )
        if author:
            embed.set_author(name=action, icon_url=author.avatar.url, url=DEFAULT_URL)

        return embed
