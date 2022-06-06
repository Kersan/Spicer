from typing import Optional
import discord
from datetime import datetime as dt


def create_embed(title: str, user: Optional[discord.User] = None,
                 description: Optional[str] = "",
                 color: Optional[int] = 0x2f3136,
                 add_date: bool = True,
                 image: str = None):
    """Służy do tworzenia i zwracania embedów."""
    embed = discord.Embed(title=title, color=color, description=description)

    # Jeżeli image istnieje, dodaje miniaturkę
    if image:
        embed.set_thumbnail(url=image)
    # Jeżeli user jest podany, tworzy authora w embedzie
    if user:
        embed.set_author(name=user.name, icon_url=user.avatar.url)
    # Jeżeli add_date jest prawdą, to dodaje timestamp
    if add_date:
        embed.timestamp = dt.utcnow()

    return embed
