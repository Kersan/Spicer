from discord.ext.commands.errors import CommandError, ObjectNotFound


class SearchNotFound(ObjectNotFound):
    """Raised when the search object is not found"""


class QueueEmpty(CommandError):
    """Raised when the queue is empty"""


class VoiceConnectionError(CommandError):
    """Raised when the bot is not connected to a voice channel"""

    def __init__(self, message: str):
        self.message = message


class PlayerNotPlaying(CommandError):
    """Raised when the player is not playing"""


class InvalidVolume(CommandError):
    """Raised when the volume is below 0 or above max"""
