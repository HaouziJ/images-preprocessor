from flask import Flask
from configparser import SectionProxy


class FlaskManager:

    def __init__(self, app: Flask, resources: SectionProxy):
        self.__app = app
        self.__resources = resources

    @property
    def app(self):
        return self.__app

    @app.setter
    def app(self, app: Flask):
        self.__app = app

    @property
    def resources(self):
        return self.__resources

    def init_flask_app(self):
        self.app.config["MONGO_URI"] = "{}://{}:{}/{}".format(self.resources["DRIVER"],
                                                              self.resources["HOST"],
                                                              self.resources["PORT"],
                                                              self.resources["NAME"])
