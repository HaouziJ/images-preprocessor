import click
from images_preprocessor.lib.logger.logger_manager import LoggerManager
from images_preprocessor.lib.resources.resource_manager import ResourceManager


@click.command()
@click.option('--imgfile', help="Overwrite image file path", default="/toto.txt")
def download_images(imgfile):

    resources = ResourceManager().get_resources()

    logger = LoggerManager("IMAGES").logger
    logger.info("HELLO I'm the logger")
    print(imgfile)
