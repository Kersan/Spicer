import logging
import sys

class Log:
    """ Zarządza logowaniem """
    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG,
                        format="%(asctime)s \u001b[7m[%(levelname)s]\u001b[0m - %(message)s",
                        datefmt="%H:%M:%S")

    def debug(name, message: str):
        """Loguje komunikat z poziomem DEBUG"""
        logging.debug(
            f"\u001b[37;1m{Log.__get_name(name)}\u001b[0m\u001b[37m: {message}\u001b[0m"
        )

    def info(name, message: str):
        """Loguje komunikat z poziomem INFO"""
        logging.info(f"\u001b[36;1m{Log.__get_name(name)}\u001b[0m\u001b[36m: {message}\u001b[0m")

    def warning(name, message: str):
        """Loguje komunikat z poziomem WARNING"""
        logging.warning(f"\u001b[31;1m{Log.__get_name(name)}\u001b[0m\u001b[31m: {message}\u001b[0m")

    def error(name, message: str):
        """Loguje komunikat z poziomem ERROR"""
        logging.error(f"\u001b[31;1m{Log.__get_name(name)}\u001b[0m\u001b[31m: {message}\u001b[0m")

    def critical(name, message: str):
        """Loguje komunikat z poziomem CRITICAL"""
        logging.critical(f"\u001b[35;1m{Log.__get_name(name)}\u001b[0m\u001b[35m: {message}\u001b[0m")

    def __get_name(name: str):
        try:
            name_parts = name.split(".")
            return name_parts[-1]
        except Exception as e:
            Log.error("LOG", f"Nie udało się pobrać nazwy modułu z: {name}! {e.with_traceback}")
