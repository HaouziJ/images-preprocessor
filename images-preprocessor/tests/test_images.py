from images_preprocessor.lib.logger.logger_manager import LoggerManager
from images_preprocessor.lib.resources.resource_manager import ResourceManager
from images_preprocessor.lib.images.image_manager import ImageManager
from configparser import SectionProxy
from logging import Logger
import os
from numpy import ndarray, divide
import pytest


def test_download_image():

    url = "https://picsum.photos/259/260"

    resources: SectionProxy = ResourceManager(env="dev").get_resources(section="DEFAULT")
    logger: Logger = LoggerManager(logger_name="TEST", log_folder=resources["LOG_DIR"], log_level="DEBUG").logger

    image_manager = ImageManager(resources=resources, logger=logger)
    _, _, shape = image_manager.download_image(image_link=url, index=0, key_folder="TEST_DIR")

    assert shape == (260, 259, 3)


def test_read_image():
    resources: SectionProxy = ResourceManager(env="dev").get_resources(section="DEFAULT")
    logger: Logger = LoggerManager(logger_name="TEST", log_level="DEBUG").logger

    image_manager = ImageManager(resources=resources, logger=logger)
    image = image_manager.read_image(os.path.join(resources["TEST_DIR"], "original_0.jpg"))
    assert image is not None


def test_encode_image():
    resources: SectionProxy = ResourceManager(env="dev").get_resources(section="DEFAULT")
    logger: Logger = LoggerManager(logger_name="TEST", log_folder=resources["LOG_DIR"], log_level="DEBUG").logger

    image_manager = ImageManager(resources=resources, logger=logger)
    image: ndarray = image_manager.read_image(os.path.join(resources["TEST_DIR"], "original_0.jpg"))

    encoded_image = image_manager.encode_image(image)
    decoded_image: ndarray = image_manager.decode_image(encoded_image)

    assert (image == decoded_image).any()


def test_md5():
    resources: SectionProxy = ResourceManager(env="dev").get_resources(section="DEFAULT")
    logger: Logger = LoggerManager(logger_name="TEST", log_folder=resources["LOG_DIR"], log_level="DEBUG").logger

    image_manager = ImageManager(resources=resources, logger=logger)
    image: ndarray = image_manager.read_image(os.path.join(resources["TEST_DIR"], "original_0.jpg"))

    encoded_image = image_manager.encode_image(image)
    _, md5 = image_manager.compute_md5(encoded_image)

    assert len(md5) == 32


def test_gray():
    resources: SectionProxy = ResourceManager(env="dev").get_resources(section="DEFAULT")
    logger: Logger = LoggerManager(logger_name="TEST", log_folder=resources["LOG_DIR"], log_level="DEBUG").logger

    image_manager = ImageManager(resources=resources, logger=logger)
    image: ndarray = image_manager.read_image(os.path.join(resources["TEST_DIR"], "original_0.jpg"))

    _, gray_image = image_manager.compute_gray_level(image)

    assert (gray_image == divide(image, 3)).any()
