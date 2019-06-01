from pymongo import MongoClient
from logging import Logger
from pymongo.database import Database
from pymongo.collection import Collection
from configparser import SectionProxy

from pymongo.errors import DuplicateKeyError


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

    @staticmethod
    def __clear_collection(collection: Collection):
        collection.drop_indexes()
        item_deleted = collection.delete_many({})
        return item_deleted.deleted_count

    def init_database(self):
        self.__client = MongoClient(self.resources["HOST"], int(self.resources["PORT"]))
        self.logger.debug(self.__client.server_info())
        self.logger.info("Initialization of the database {}...".format(self.resources["NAME"]))
        self.__database: Database = self.__client[self.resources["NAME"]]
        return self.__database.name

    def get_collection(self, collection_name: str, index_collection: str = None, overwrite: bool = False):
        self.logger.info("Getting collection {}...".format(collection_name))
        collection = self.__database[collection_name]
        if overwrite:
            self.logger.debug("Deleting {} items...".format(self.__clear_collection(collection=collection)))
        if index_collection:
            self.logger.info("Creating index on {}...".format(index_collection))
            collection.create_index(index_collection, unique=True)
        self.logger.debug(self.__database.list_collection_names())
        return collection

    def insert_many_documents(self, collection: Collection, documents: list):
        try:
            result = collection.insert_many(documents)
            return "success", result.inserted_ids
        except Exception as error:
            self.logger.exception(error)
            return "error", []

    def insert_one_document(self, collection: Collection, document: dict):
        try:
            result = collection.insert_one(document)
            return "success", result.inserted_id
        except DuplicateKeyError as error:
            self.logger.warning("Key already exists {}".format(error))
            return "error", ""
        except Exception as error:
            self.logger.exception(error)
            return "error", ""


