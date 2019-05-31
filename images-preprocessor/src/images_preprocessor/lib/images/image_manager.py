from urllib.error import HTTPError
import urllib.request as req
from logging import Logger
from images_preprocessor.lib.common.common import retry
import os
from cv2 import imread, imwrite
import hashlib
from numpy import divide, ndarray
from configparser import SectionProxy
from datetime import datetime


class ImageManager:

    def __init__(self, img_url_file: str, resources: SectionProxy, logger: Logger = None):
        self.__img_url_file = img_url_file
        self.__resources = resources
        self.__logger = logger
        self.__img_url_list: list = []
        self.__documents: list = []

    @property
    def img_url_file(self):
        return self.__img_url_file

    @img_url_file.setter
    def img_url_file(self, img_url_file: str):
        self.__img_url_file = img_url_file

    @property
    def resources(self):
        return self.__resources

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, logger):
        self.__logger = logger

    @property
    def documents(self):
        return self.__documents

    @retry(HTTPError, tries=2, delay=3, backoff=1, logger=None)
    def __url_open(self, request):
        try:
            response = req.urlopen(request)
            return response
        except HTTPError as error:
            if error.code == 404:
                self.logger.error(error)
                return None
            elif error.code == 400:
                self.logger.error(error)
            else:
                raise error
        except Exception as e:
            self.logger.exception(e)

    def __download_image(self, image_link: str, index: int):
        self.logger.debug("Downloading image number {}...".format(index))
        self.logger.debug("Link {}...".format(image_link))
        try:
            request = req.Request(image_link)
            response = self.__url_open(request)

            if response is not None:
                image = response.read()
                image_path = os.path.join(self.resources["ORIGINAL_IMAGE_DIR"], "original_{}.jpg".format(index))
                with open(image_path, 'wb') as output:
                    self.logger.debug("Writing image to {}...".format(image_path))
                    output.write(image)
                return image
            else:
                return "error"
        except ValueError:
            self.logger.error("Bad image link: {}".format(image_link))
            return "error"
        except Exception as error:
            self.logger.error(error)
            return "error"

    def __read_image(self, image_file: str):
        try:
            self.logger.debug("Reading image {}...".format(image_file))
            image = imread(image_file)
            return image
        except Exception as e:
            self.logger.exception(e)
            return None

    def __write_image(self, image_file_path: str, image: ndarray):
        try:
            self.logger.debug("Writing image to {}...".format(image_file_path))
            state = imwrite(image_file_path, image)
            self.logger.debug("[DONE] State: {}...".format(state))
            return state
        except Exception as e:
            self.logger.exception(e)
            return None

    def __compute_md5(self, image: ndarray):
        md5_hash = hashlib.md5()
        try:
            self.logger.debug("Compute MD5 => Image shape: {}".format(image.shape))
            md5_hash.update(image)
            return md5_hash.hexdigest()
        except TypeError as type_error:
            self.logger.error("Wrong given type to hash with md5: {}".format(type_error))
            return ""

    def __compute_gray_level(self, image: ndarray):
        try:
            return divide(image, 3)
        except Exception as error:
            self.logger.exception(error)
            return None

    def __get_images_link(self):
        with open(self.img_url_file, "r") as file:
            self.logger.info("Parsing urls from file {}...".format(self.img_url_file))
            self.img_url_list: list = file.read().split("\n")

    def collect_images(self):
        self.__get_images_link()
        url_length: int = len(self.img_url_list)
        self.logger.info("Starting downloading for {} images...".format(url_length))
        for url, index in zip(self.img_url_list, range(url_length)):
            image = self.__download_image(url, index)
            self.logger.debug({"url": url, "timestamp": datetime.now().strftime("%Y%m%d%H%M")})
            self.documents.append({"url": url, "image": image, "timestamp": datetime.now().strftime("%Y%m%d%H%M")})
        return self.documents
