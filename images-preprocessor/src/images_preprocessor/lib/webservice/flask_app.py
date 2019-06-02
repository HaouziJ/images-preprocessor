from flask import Flask
from flask import render_template, send_file
from flask_pymongo import PyMongo
import os
from configparser import SectionProxy
from images_preprocessor.lib.resources.resource_manager import ResourceManager
from images_preprocessor.lib.logger.logger_manager import LoggerManager
from images_preprocessor.lib.webservice.flask_manager import FlaskManager
from logging import Logger
import pandas
import io
import seaborn as sns
import matplotlib.pyplot as plt

resources: SectionProxy = ResourceManager(env=os.environ["ENV"]).get_resources(section="MONGODB")
logger: Logger = LoggerManager(logger_name="IMAGE", log_folder=resources["LOG_DIR"], log_level="DEBUG").logger


app = Flask(__name__)

flask_instance = FlaskManager(app=app, resources=resources)
flask_instance.init_flask_app()

mongo = PyMongo(flask_instance.app)


@app.route('/home')
def index():
    results = mongo.db.target_images.find()
    return render_template("index.html", data=results)


@app.route("/image/<string:md5>")
def image(md5):
    # 3afd392d481cb31625f86d87e38b7cbc
    results = mongo.db.target_images.find_one_or_404({"md5": md5})
    return send_file(io.BytesIO(results["image"]), mimetype='image/jpg')


@app.route('/transfo_per_minute.png')
def transformation_per_minute():

    transformation = mongo.db.monitoring.find()

    df_transformation = pandas.DataFrame(list(transformation))

    sns.catplot(y="timestamp", hue="state", kind="count", palette="pastel", edgecolor=".6", data=df_transformation)

    output = io.BytesIO()
    plt.savefig(output, format='png')
    output.seek(0)

    return send_file(output,  mimetype='image/png')


@app.route("/")
@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html")
