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
@click.option('--env', envvar='ENV', help="Environment in which run the function", default="dev")
def main_init_directory_structure(env: str):
    """
    This function will create all directory needed for the project

    :param env: Environment that will load the correct property file
    """
    resources: SectionProxy = ResourceManager(env=env).get_resources()
    logger: Logger = LoggerManager(logger_name="DIRECTORY", log_folder=resources["LOG_DIR"], log_level="DEBUG").logger

    init_directory_structure(resources=resources, logger=logger)


@click.command()
@click.option('--env', envvar='ENV', help="Environment in which run the function", default="dev")
@click.option('--imgfile', help="Overwrite image file path", default="")
@click.option('--loglevel', help="Set the logging level", default="DEBUG")
@click.option('--overwrite', help="Overwrite the collection before insertion", default=True)
def main_collect_insert_images(env: str, imgfile: str, loglevel: str = "DEBUG", overwrite: bool = True):
    """
    This function will create the database if not exists and a collection in a mongoDB database. Then it will
    download all images from the image file provided, they will be wrote on file system of the Docker.
    Finally all images will be stored inside the collection without index, with their url, image shape,
    the state of download and the insertion timestamp.

    :param env: Environment that will load the correct property file
    :param imgfile: Path to the image file containing URLs
    :param loglevel: Logging level for message generation
    :param overwrite: Truncate the collection or not
    """

    resources: SectionProxy = ResourceManager(env=env).get_resources()
    db_resources: SectionProxy = ResourceManager(env=env).get_resources(section="MONGODB")

    logger: Logger = LoggerManager(logger_name="IMAGE", log_folder=resources["LOG_DIR"], log_level=loglevel).logger
    db_logger: Logger = LoggerManager(logger_name="MONGO", log_folder=resources["LOG_DIR"], log_level=loglevel).logger
    main_logger: Logger = LoggerManager(logger_name="MAIN", log_folder=resources["LOG_DIR"], log_level=loglevel).logger

    image_file_path: str = imgfile if imgfile != "" else os.path.join(resources["DATA_DIR"], "urls.txt")

    image_manager = ImageManager(resources=resources, img_url_file=image_file_path, logger=logger)
    mongo_manager = MongoManager(resources=db_resources, logger=db_logger)

    mongo_manager.init_database()
    collection: Collection = mongo_manager.get_collection(collection_name="original_images", overwrite=overwrite)
    documents: list = image_manager.collect_images()

    state, result_ids = mongo_manager.insert_many_documents(collection=collection, documents=documents)

    main_logger.info("Insertion state: {} with {} insertion".format(state, len(result_ids)))
    main_logger.debug("Ids inserted: {}".format(result_ids))


@click.command()
@click.option('--env', envvar='ENV', help="Environment in which run the function", default="dev")
@click.option('--loglevel', help="Set the logging level", default="DEBUG")
@click.option('--overwrite', help="Overwrite the collection before insertion", default=True)
def main_compute_insert_md5_and_gray(env: str, loglevel: str = "DEBUG", overwrite: bool = True):
    """
    This function will create the database if not exists and two collection in a mongoDB database. Then it will
    get all images from the original images collection and it will compute the md5 and the gray level of each image.
    All information about transformation state will be stored in one monitoring collection containing url, state and
    timestamp, and a second target collection containing md5, new image, size and insertion timestamp.

    :param env: Environment that will load the correct property file
    :param loglevel: Logging level for message generation
    :param overwrite: Truncate the collection or not
    """

    resources: SectionProxy = ResourceManager(env=env).get_resources()
    db_resources: SectionProxy = ResourceManager(env=env).get_resources(section="MONGODB")

    logger: Logger = LoggerManager(logger_name="IMAGE", log_folder=resources["LOG_DIR"], log_level=loglevel).logger
    db_logger: Logger = LoggerManager(logger_name="MONGO", log_folder=resources["LOG_DIR"], log_level=loglevel).logger
    main_logger: Logger = LoggerManager(logger_name="MAIN", log_folder=resources["LOG_DIR"], log_level=loglevel).logger

    image_manager = ImageManager(resources=resources, logger=logger)
    mongo_manager = MongoManager(resources=db_resources, logger=db_logger)

    mongo_manager.init_database()
    original_collection: Collection = mongo_manager.get_collection(collection_name="original_images")
    target_collection: Collection = mongo_manager.get_collection(collection_name="target_images",
                                                                 index_collection="md5", overwrite=overwrite)
    monitoring_collection: Collection = mongo_manager.get_collection(collection_name="monitoring", overwrite=overwrite)

    image_documents = original_collection.find()
    documents, errors = image_manager.collect_gray_and_md5(documents=image_documents)

    main_logger.info("Inserting {} documents...".format(len(documents)))
    for document in documents:
        main_logger.debug("Inserting document md5: {}, size:{}...".format(document["md5"], document["size"]))
        mongo_manager.insert_one_document(collection=target_collection, document=document)

    main_logger.info("Inserting {} monitoring messages...".format(len(errors)))
    state, _ = mongo_manager.insert_many_documents(collection=monitoring_collection, documents=errors)
    main_logger.info("Final state for monitoring insert: {}".format(state))



