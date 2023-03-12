from discord.ext.commands.errors import CommandError, ObjectNotFound


class SearchNotFound(ObjectNotFound):
    pass


class QueueEmpty(CommandError):
    pass


class VoiceConnectionError(CommandError):
    def __init__(self, message: str):
        self.message = message


class PlayerNotPlaying(CommandError):
    pass


class VolumeBelowZero(CommandError):
    pass
