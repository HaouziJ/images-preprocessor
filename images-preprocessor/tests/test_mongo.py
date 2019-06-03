from images_preprocessor.lib.logger.logger_manager import LoggerManager
from images_preprocessor.lib.resources.resource_manager import ResourceManager
from configparser import SectionProxy
from logging import Logger
from images_preprocessor.lib.mongo.mongo_manager import MongoManager
from pymongo.collection import Collection


def test_mongodb():

    resources: SectionProxy = ResourceManager(env="dev").get_resources(section="MONGODB")
    logger: Logger = LoggerManager(logger_name="TEST", log_folder=resources["LOG_DIR"], log_level="DEBUG").logger
    mongo_manager = MongoManager(resources=resources, logger=logger)

    database = mongo_manager.init_database()

    assert database == resources["NAME"]


def test_insertion():
    resources: SectionProxy = ResourceManager(env="dev").get_resources(section="MONGODB")
    logger: Logger = LoggerManager(logger_name="TEST", log_folder=resources["LOG_DIR"], log_level="INFO").logger
    mongo_manager = MongoManager(resources=resources, logger=logger)

    mongo_manager.init_database()

    collection: Collection = mongo_manager.get_collection(collection_name="unit_test", overwrite=True)
    document = {"name": "unit_test", "number": 35}

    state, _ = mongo_manager.insert_one_document(collection=collection, document=document)

    assert state == "success"


def test_find():
    resources: SectionProxy = ResourceManager(env="dev").get_resources(section="MONGODB")
    logger: Logger = LoggerManager(logger_name="TEST", log_folder=resources["LOG_DIR"], log_level="INFO").logger
    mongo_manager = MongoManager(resources=resources, logger=logger)

    mongo_manager.init_database()

    collection: Collection = mongo_manager.get_collection(collection_name="unit_test")

    inserted_object = collection.find_one({"name": "unit_test"})

    assert inserted_object["number"] == 35
