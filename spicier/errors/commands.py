from discord.ext.commands.errors import CommandError


class WrongArgument(CommandError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
