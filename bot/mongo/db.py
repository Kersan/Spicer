import pymongo
import sys

from bot.mongo.dblogs import MongoLogs


class Mongo(MongoLogs):
    def __init__(self, uri: str):
        self.uri = uri

        # Obiekt bazy danych
        # Dodatkowo w funkcji sprawdzane jest połączenie i dodawane
        # są wszystkie kolekcje logów
        self.db = self.setup()

        # Konstruktor dla klasy z obsługą kolekcji logów
        super().__init__(self.db)

    def setup(self):
        """ Metoda startowa
        1. Nawiązuje połączenie z bazą
        2. Zwraca obiekt bazy 
        """

        global client
        client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=5000)

        if self.test_connection(client):
            # > "If an operation fails because of a network error..."
            # "...client reconnects in the background."

            try:
                dblist = client.list_database_names()
            except:
                sys.exit("Nie udało się pobrać bazy danych.")

            if "test" not in dblist:
                return client["test"]

            else:
                return client.get_database("test")

        else:
            # W przypadku problemu z Mongosem, proces jest zabijany
            sys.exit("Nie udało się naziązać połączenia z bazą!")

    def get_names(self):
        if client:
            return self.db.list_collection_names()

    @staticmethod
    def test_connection(c):
        try:
            c.admin.command('ping')
        except Exception as e:
            print(f"Test połączenia nie powiódł się:\n{e}")
            return False

        return True
