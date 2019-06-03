from urllib.error import HTTPError
import urllib.request as req
from logging import Logger
from images_preprocessor.lib.common.common import retry
import os
from cv2 import imread, imwrite, imencode, imdecode, IMREAD_COLOR
import hashlib
from numpy import divide, ndarray
from configparser import SectionProxy
from datetime import datetime
from numpy import frombuffer, uint8


class ImageManager:

    def __init__(self, resources: SectionProxy, img_url_file: str = None, logger: Logger = None):
        """
        This class handle all operations applied on images, like read, write, encode, decode
        or compute gray level and md5.

        :param resources: Resources instance from the resource manager
        :param img_url_file: Path of the image file containing urls
        :param logger: Logger instance from logger manager
        """

        self.__img_url_file = img_url_file
        self.__resources = resources
        self.__logger = logger
        self.__img_url_list: list = []
        self.__documents: list = []
        self.__monitoring: list = []

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
    def monitoring(self):
        return self.__monitoring

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

    def download_image(self, image_link: str, index, key_folder: str = "ORIGINAL_IMAGE_DIR"):
        """
        This function will download an image, write it to the file system and return the image, the image shape
        and the state

        :param image_link: URL link of the image
        :param index: Index or suffix name of the image name
        :param key_folder: Key of the property file giving the folder path to save the image
        :return: state: str
        :return: image: ndarray
        :return: shape: tuple
        """
        self.logger.debug("Downloading image number {}...".format(index))
        self.logger.debug("Link {}...".format(image_link))
        try:
            request = req.Request(image_link)
            response = self.__url_open(request)

            if response is not None:
                byte_image = response.read()
                image_path = os.path.join(self.resources[key_folder], "original_{}.jpg".format(index))
                self.logger.debug("Writing image to {}...".format(image_path))
                with open(image_path, 'wb') as output:
                    output.write(byte_image)
                image: ndarray = self.decode_image(byte_image)
                return "success", image, image.shape
            else:
                return "error", "error", ()
        except ValueError:
            self.logger.error("Bad image link: {}".format(image_link))
            return "error", ()
        except Exception as error:
            self.logger.error(error)
            return "error", ()

    def read_image(self, image_file: str):
        try:
            self.logger.debug("Reading image {}...".format(image_file))
            image = imread(image_file)
            return image
        except Exception as e:
            self.logger.exception(e)
            return None

    def write_image(self, image_file_path: str, image: ndarray):
        try:
            self.logger.debug("Writing image to {}...".format(image_file_path))
            state = imwrite(image_file_path, image)
            self.logger.debug("[DONE] State: {}...".format(state))
            return state
        except Exception as e:
            self.logger.exception(e)
            return None

    def compute_md5(self, image: bytes):
        """
        This function will compute the md5 of a binary image and return the state and the md5 hash

        :param image: Image as bytes to compute md5
        :return: state: str
        :return: md5: str
        """
        md5_hash = hashlib.md5()
        try:
            md5_hash.update(image)
            return "success", md5_hash.hexdigest()
        except TypeError as type_error:
            self.logger.error("Wrong given type to hash with md5: {}".format(type_error))
            return "error", ""

    def compute_gray_level(self, image: ndarray):
        """
        This function will compute the gray level of an image. It will divide by 3 all the image array, and return it
        with the transformation state.

        :param image: Image as an array
        :return: state: str
        :return: image: ndarray
        """
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
    def decode_image(image):
        try:
            return imdecode(frombuffer(image, uint8), IMREAD_COLOR)
        except AttributeError:
            return image

    @staticmethod
    def encode_image(image: ndarray):
        try:
            return imencode('.jpg', image)[1].tostring()
        except TypeError:
            return image
        except AttributeError:
            return image

    def collect_images(self):
        """
        This function will download all images of the image file and insert them in a document list with their
        url, shape, state and insertion timestamp.

        :return: documents: list
        """
        self.__get_images_link()
        url_length: int = len(self.img_url_list)
        self.logger.info("Starting downloading for {} images...".format(url_length))
        for url, index in zip(self.img_url_list, range(url_length)):
            state, image, shape = self.download_image(url, index)
            self.logger.debug({"url": url, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            self.documents.append({"url": url,
                                   "image": self.encode_image(image),
                                   "shape": shape,
                                   "state": state,
                                   "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        return self.documents

    def collect_gray_and_md5(self, documents: list):
        """
        This function will get all images of the document list, compute the gray level and md5, write the new image
        on docker file system naming them with the md5, and finally insert all images with success state in a collection
        and information about transformation in another monitoring collection.

        :param documents: List of documents containing original images
        :return:
        """
        for document in documents:
            md5_state, md5 = self.compute_md5(document["image"])
            gray_state, gray_image = self.compute_gray_level(self.decode_image(document["image"]))
            self.write_image(os.path.join(self.resources["GRAY_IMAGE_DIR"], "{}.jpg".format(md5)), gray_image)

            self.logger.debug("{} and {}".format(md5_state, gray_state))

            if md5_state == "success" and gray_state == "success":
                size = gray_image.shape[:2]
                self.documents.append({"md5": md5,
                                       "image": self.encode_image(gray_image),
                                       "size": size,
                                       "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                self.monitoring.append({"url": document["url"],
                                        "state": "success",
                                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            else:
                self.monitoring.append({"url": document["url"],
                                        "state": "error",
                                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        return self.documents, self.monitoring
