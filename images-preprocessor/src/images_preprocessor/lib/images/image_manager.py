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
from numpy import frombuffer, uint8, reshape


class ImageManager:

    def __init__(self, resources: SectionProxy, img_url_file: str = None, logger: Logger = None):
        self.__img_url_file = img_url_file
        self.__resources = resources
        self.__logger = logger
        self.__img_url_list: list = []
        self.__documents: list = []
        self.__errors: list = []

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

    @property
    def errors(self):
        return self.__errors

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
                byte_image = response.read()
                image_path = os.path.join(self.resources["ORIGINAL_IMAGE_DIR"], "original_{}.jpg".format(index))
                with open(image_path, 'wb') as output:
                    self.logger.debug("Writing image to {}...".format(image_path))
                    output.write(byte_image)
                image: ndarray = self.__read_image(image_path)
                return image, image.shape
            else:
                return "error", ()
        except ValueError:
            self.logger.error("Bad image link: {}".format(image_link))
            return "error", ()
        except Exception as error:
            self.logger.error(error)
            return "error", ()

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
            md5_hash.update(image)
            return "success", md5_hash.hexdigest()
        except TypeError as type_error:
            self.logger.error("Wrong given type to hash with md5: {}".format(type_error))
            return "error", ""

    def __compute_gray_level(self, image: ndarray):
        try:
            return "success", divide(image, 3)
        except TypeError:
            self.logger.error("Wrong given type to divide: {}".format(type(image)))
            return "error", None
        except Exception as error:
            self.logger.exception(error)
            return "error", None

    def __get_images_link(self):
        with open(self.img_url_file, "r") as file:
            self.logger.info("Parsing urls from file {}...".format(self.img_url_file))
            self.img_url_list: list = [url for url in file.read().split("\n") if url.startswith("http")]

    @staticmethod
    def __decode_image(image: bytes, shape: tuple):
        try:
            return reshape(frombuffer(image, dtype=uint8), shape)
        except AttributeError:
            return image

    @staticmethod
    def __encode_image(image: ndarray):
        try:
            return image.tobytes(order="C")
        except AttributeError:
            return image

    def collect_images(self):
        self.__get_images_link()
        url_length: int = len(self.img_url_list)
        self.logger.info("Starting downloading for {} images...".format(url_length))
        for url, index in zip(self.img_url_list, range(url_length)):
            image, shape = self.__download_image(url, index)
            self.logger.debug({"url": url, "timestamp": datetime.now().strftime("%Y%m%d%H%M")})
            self.documents.append({"url": url,
                                   "image": self.__encode_image(image),
                                   "shape": shape,
                                   "timestamp": datetime.now().strftime("%Y%m%d%H%M")})
        return self.documents

    def collect_gray_and_md5(self, documents: list):
        for document in documents:
            md5_state, md5 = self.__compute_md5(document["image"])
            gray_state, gray_image = self.__compute_gray_level(self.__decode_image(document["image"],
                                                                                   document["shape"]))

            self.logger.debug("{} and {}".format(md5_state, gray_state))

            if md5_state == "success" and gray_state == "success":
                size = gray_image.shape[:2]
                self.documents.append({"md5": md5,
                                       "image": self.__encode_image(gray_image),
                                       "size": size,
                                       "timestamp": datetime.now().strftime("%Y%m%d%H%M")})
            else:
                self.errors.append({"url": document["url"],
                                    "md5_state": md5_state,
                                    "gray_state": gray_state,
                                    "timestamp": datetime.now().strftime("%Y%m%d%H%M")})
        return self.documents, self.errors
