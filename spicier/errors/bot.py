class BadConfig(Exception):
    """Raised when the config is invalid"""

    def __init__(self, cause: Exception):
        self.cause = cause
