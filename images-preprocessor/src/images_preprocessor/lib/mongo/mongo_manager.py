from pymongo import MongoClient
from logging import Logger
from pymongo.database import Database
from pymongo.collection import Collection
from configparser import SectionProxy


class MongoManager:
    def __init__(self, resources: SectionProxy, logger: Logger = None):
        self.__resources: SectionProxy = resources
        self.__client: MongoClient = None
        self.__database: Database = None
        self.__logger: Logger = logger

    @property
    def resources(self):
        return self.__resources

    @resources.setter
    def resources(self, resources: SectionProxy):
        self.__resources = resources

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, logger: Logger):
        self.__logger = logger

    def init_database(self):
        self.__client = MongoClient(self.resources["HOST"], int(self.resources["PORT"]))
        self.logger.debug(self.__client.server_info())
        self.logger.info("Initialization of the database {}...".format(self.resources["NAME"]))
        self.__database: Database = self.__client[self.resources["NAME"]]
        return self.__database.name

    def create_collection(self, collection_name: str):
        self.logger.info("Creating new collection {}...".format(collection_name))
        collection = self.__database[collection_name]
        self.logger.debug(self.__database.list_collection_names())
        return collection

    def insert_documents(self, collection: Collection, documents: list):
        try:
            result = collection.insert_many(documents)
            return "done", result.inserted_ids
        except Exception as error:
            self.logger.exception(error)
            return "error", []


