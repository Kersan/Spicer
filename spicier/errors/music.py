from discord.ext.commands.errors import CommandError, ObjectNotFound


class SearchNotFound(ObjectNotFound):
    pass


class QueueEmpty(CommandError):
    pass