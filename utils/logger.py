import logging
import sys

class Logging:
    """ Zarządza logowaniem """

    print([logging.getLogger(name) for name in logging.root.manager.loggerDict])

    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG,
                        format="%(asctime)s \u001b[7m[%(levelname)s]\u001b[0m - %(message)s",
                        datefmt="%H:%M:%S")
    @staticmethod
    def debug(name, message: str):
        """Loguje komunikat z poziomem DEBUG"""
        logging.debug(f"\u001b[37;1m{name[4:]}\u001b[0m\u001b[37m: {message}\u001b[0m")

    @staticmethod
    def info(name, message: str):
        """Loguje komunikat z poziomem INFO"""
        logging.info(f"\u001b[36;1m{name[4:]}\u001b[0m\u001b[36m: {message}\u001b[0m")

    @staticmethod
    def warning(name, message: str):
        """Loguje komunikat z poziomem WARNING"""
        logging.warning(f"\u001b[31;1m{name[4:]}\u001b[0m\u001b[31m: {message}\u001b[0m")

    @staticmethod
    def error(name, message: str):
        """Loguje komunikat z poziomem ERROR"""
        logging.error(f"\u001b[31;1m{name[4:]}\u001b[0m\u001b[31m: {message}\u001b[0m")

    @staticmethod
    def critical(name, message: str):
        """Loguje komunikat z poziomem CRITICAL"""
        logging.critical(f"\u001b[35;1m{name[4:]}\u001b[0m\u001b[35m: {message}\u001b[0m")
