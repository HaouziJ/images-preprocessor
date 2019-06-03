import configparser
import os


class ResourceManager:

    def __init__(self, env: str = "dev", resources_folder: str = os.path.dirname(__file__)):
        """
        This class is used to generate object to access on properties file
        according on environment variable giving as parameter

        :param env: Prefix value of the property file
        :param resources_folder: Resource folder path
        """
        self.__env = env
        self.__resources_folder = resources_folder
        self.__config = configparser.ConfigParser()
        self.__config_file_name = None

    @property
    def config(self):
        return self.__config

    @property
    def env(self):
        return self.__env

    @env.setter
    def env(self, env: str):
        self.__env = env

    @property
    def resources_folder(self):
        return self.__resources_folder

    @resources_folder.setter
    def resources_folder(self, resources_folder: str):
        self.__resources_folder = resources_folder

    @property
    def config_file_name(self):
        self.__config_file_name: str = os.path.join(self.resources_folder, "{}.properties".format(self.env))
        return self.__config_file_name

    def get_resources(self, section: str = "DEFAULT"):
        self.config.read(self.config_file_name)
        return self.config[section]

    def write_new_property(self, key, value, section="DEFAULT"):
        with open(self.config_file_name, "w") as config_file:
            self.get_resources(section)[key] = value
            self.config.write(config_file)
