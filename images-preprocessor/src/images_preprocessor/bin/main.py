import click
from images_preprocessor.lib.logger.logger_manager import LoggerManager
from images_preprocessor.lib.resources.resource_manager import ResourceManager
from images_preprocessor.lib.images.image_manager import ImageManager
import os


@click.command()
@click.option('--env', help="Environment in which run the function", default="dev")
@click.option('--imgfile', help="Overwrite image file path", default="")
def download_images(env: str, imgfile: str):

    resources = ResourceManager(env).get_resources()
    logger = LoggerManager("IMAGES", resources["LOG_DIR"], log_level="DEBUG").logger

    image_file_path = imgfile if imgfile != "" else os.path.join(resources["DATA_DIR"], "urls.txt")

    image_manager = ImageManager(image_file_path, resources, logger)
    image_manager.download_images()

