from discord.ext.commands.errors import CommandError


class WrongArgument(CommandError):
    """Raised when the argument is invalid"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
