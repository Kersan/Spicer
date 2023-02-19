from discord import Embed, User
from discord.ext import commands


class MusicSuccess(Embed):
    def __init__(
        self,
        author: User,
        action: str,
        title: str,
        description: str = None,
        url: str = None,
        thumbnail: str = None,
        color=0x313338,
    ):
        super().__init__(
            url=url,
            color=color,
            title=title,
            description=description,
        )
        self.set_author(name=action, icon_url=author.avatar_url)
        self.set_thumbnail(url=thumbnail)
