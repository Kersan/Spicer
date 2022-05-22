import pymongo
from datetime import datetime


class MongoLogs:
    def __init__(self, db: pymongo.database.Database):
        self.cMember = None
        self.cGateway = None
        self.cMessage = None
        self.db = db

        # Dodanie kolekcji
        self.add_collections()

    def add_collections(self):
        clist = self.db.list_collection_names()

        # cMessage
        if "Message" in clist:
            self.cMessage = self.db.get_collection("Message")
        else:
            self.cMessage = self.db["Message"]

        # cGateway
        if "Gateway" in clist:
            self.cGateway = self.db.get_collection("Gateway")
        else:
            self.cGateway = self.db["Gateway"]

        # cMember
        if "Member" in clist:
            self.cMember = self.db.get_collection("Member")
        else:
            self.cMember = self.db["Member"]

    def message_deleted(self, guild_id: int, user_id: int, before: str,
                        action: int = -1, time: datetime = datetime.now()):
        """ Usadawia zdarzenie o usunięciu wiadomości w bazie. """

        # Kontent do bazy:
        json = {
            "GuildID": guild_id,
            "UserID": user_id,
            "Action": action,
            "Time": time,
            "Before": before}

        _id = self.cMessage.insert_one(json)
        return _id.inserted_id

    def message_edited(self, guild_id: int, user_id: int,
                       before: str, after: str, action: int = 1, time: datetime = datetime.now()):
        """ Usadawia zdarzenie o edycji wiadomości w bazie. """

        # Kontent do bazy:
        json = {
            "GuildID": guild_id,
            "UserID": user_id,
            "Action": action,
            "Time": time,
            "Before": before,
            "After": after}

        _id = self.cMessage.insert_one(json)
        return _id.inserted_id
