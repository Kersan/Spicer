from .success import MusicSuccess


class MusicEmbed:
    @staticmethod
    def success(
        author,
        action,
        title=None,
        description=None,
        url=None,
        thumbnail=None,
        color=3224376,
    ):
        return MusicSuccess()
