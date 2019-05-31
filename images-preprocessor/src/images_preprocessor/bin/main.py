import click
from images_preprocessor.lib.logger.logger_manager import LoggerManager
from images_preprocessor.lib.resources.resource_manager import ResourceManager
from images_preprocessor.lib.images.image_manager import ImageManager
from images_preprocessor.lib.mongo.mongo_manager import MongoManager
from images_preprocessor.lib.common.common import init_directory_structure
import os
from logging import Logger
from configparser import SectionProxy
from pymongo.collection import Collection


@click.command()
@click.option('--env', help="Environment in which run the function", default="dev")
def main_init_directory_structure(env: str):

    resources: SectionProxy = ResourceManager(env).get_resources()
    logger: Logger = LoggerManager("DIRECTORY", resources["LOG_DIR"], log_level="DEBUG").logger

    init_directory_structure(resources, logger)


@click.command()
@click.option('--env', help="Environment in which run the function", default="dev")
@click.option('--imgfile', help="Overwrite image file path", default="")
def main_collect_insert_images(env: str, imgfile: str):

    resources: SectionProxy = ResourceManager(env).get_resources()
    db_resources: SectionProxy = ResourceManager(env).get_resources(section="MONGODB")

    logger: Logger = LoggerManager("IMAGE", resources["LOG_DIR"], log_level="DEBUG").logger
    db_logger: Logger = LoggerManager("MONGO", resources["LOG_DIR"], log_level="DEBUG").logger
    main_logger: Logger = LoggerManager("MAIN", resources["LOG_DIR"], log_level="DEBUG").logger

    image_file_path: str = imgfile if imgfile != "" else os.path.join(resources["DATA_DIR"], "urls.txt")

    image_manager = ImageManager(image_file_path, resources, logger)
    mongo_manager = MongoManager(db_resources, db_logger)

    mongo_manager.init_database()
    collection: Collection = mongo_manager.create_collection("original_images")
    documents: list = image_manager.collect_images()

    state, result_ids = mongo_manager.insert_documents(collection, documents)

    main_logger.info("Insertion state: {} with {} insertion".format(state, len(result_ids)))
    main_logger.debug("Ids inserted: {}".format(result_ids))


