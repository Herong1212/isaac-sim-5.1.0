from abc import ABC, abstractmethod
from pymongo import MongoClient
from ..object_caption.generate_object_caption import DB_NAME, COLLECTION_NAME


# TODO (METROPERF-844): Please add unittests for this interface
class DB(ABC):
    @abstractmethod
    def insert(self, data):
        pass

    @abstractmethod
    def find(self, query):
        pass


class MongoDB(DB):
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], str):
            # Constructor with just URI string
            mongodb_uri = args[0]
            client = MongoClient(mongodb_uri)
            db = client[DB_NAME]
            self.collection = db[COLLECTION_NAME]
        else:
            # Original constructor with individual parameters
            host, username, password, database, collection, options = args
            mongodb_uri = f"mongodb+srv://{username}:{password}@{host}/?{options}"
            client = MongoClient(mongodb_uri)
            db = client[database]
            self.collection = db[collection]

    def insert(self, data):
        self.collection.insert_one(data)

    def find(self, query):
        return self.collection.find(query)
