from flask import Flask
from flask import render_template
from flask_pymongo import PyMongo
import os
from configparser import SectionProxy
from images_preprocessor.lib.resources.resource_manager import ResourceManager
from images_preprocessor.lib.logger.logger_manager import LoggerManager
from logging import Logger
import pandas

resources: SectionProxy = ResourceManager(env=os.environ["ENV"]).get_resources(section="MONGODB")
logger: Logger = LoggerManager(logger_name="IMAGE", log_folder=resources["LOG_DIR"], log_level="DEBUG").logger

app = Flask(__name__)
app.config["MONGO_URI"] = "{}://{}:{}/{}".format(resources["DRIVER"],
                                                 resources["HOST"],
                                                 resources["PORT"],
                                                 resources["NAME"])

mongo = PyMongo(app)


@app.route("/")
def index():
    results = mongo.db.target_images.find()
    return render_template("index.html", data=results)


@app.route("/image/<string:md5>")
def image(md5):
    results = mongo.db.target_images.find_one_or_404({"md5": md5})
    return render_template("image.html", md5=results["md5"])


@app.route("/monitoring")
def monitoring():
    total = mongo.db.monitoring.find({}).count()

    md5_success = mongo.db.monitoring.find({"md5_state": "success"}).count()
    md5_error = mongo.db.monitoring.find({"md5_state": "error"}).count()

    gray_success = mongo.db.monitoring.find({"gray_state": "success"}).count()
    gray_error = mongo.db.monitoring.find({"gray_state": "error"}).count()

    md5_count = mongo.db.monitoring.aggregate([
        {'$group':
            {'_id': {'timestamp': "$timestamp", "md5_state": "$md5_state"}, 'count': {'$sum': 1}}
         }
    ])

    gray_count = mongo.db.monitoring.aggregate([
        {'$group':
            {'_id': {'timestamp': "$timestamp", "gray_state": "$gray_state"}, 'count': {'$sum': 1}}
         }
    ])

    stats = mongo.db.monitoring.find()

    df = pandas.DataFrame(list(stats)).groupby(["timestamp", "md5_state", "gray_state"]).count()

    return render_template("monitoring.html", md5_success=md5_success,
                           md5_error=md5_error,
                           gray_success=gray_success,
                           gray_error=gray_error,
                           total=total,
                           md5_count=md5_count,
                           gray_count=gray_count, df=df)
