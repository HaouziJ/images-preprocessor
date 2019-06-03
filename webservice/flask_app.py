from flask import Flask
from flask import render_template, send_file
from flask_pymongo import PyMongo
import pandas
import io
import seaborn as sns
import matplotlib.pyplot as plt
import os

debug = os.environ.get('Foo') if os.environ.get('Foo') else False

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo-database:27017/image_db"
mongo = PyMongo(app)


@app.route("/image/<string:md5>")
def image(md5):
    # 3afd392d481cb31625f86d87e38b7cbc
    results = mongo.db.target_images.find_one_or_404({"md5": md5})
    return send_file(io.BytesIO(results["image"]), mimetype='image/jpg')


@app.route('/monitoring')
def transformation_per_minute():

    transformation = mongo.db.monitoring.find()

    df_transformation = pandas.DataFrame(list(transformation))

    sns.catplot(y="timestamp", hue="state", kind="count", palette="pastel", edgecolor=".6", data=df_transformation)

    output = io.BytesIO()
    plt.savefig(output, format='png')
    output.seek(0)

    return send_file(output,  mimetype='image/png')


@app.route("/")
def index():
    results = mongo.db.target_images.find()
    transformation_s = mongo.db.monitoring.find({"state": "success"}).count()
    transformation_e = mongo.db.monitoring.find({"state": "error"}).count()
    return render_template("index.html", transformation_s=transformation_s,
                           transformation_e=transformation_e, results=results)


if __name__ == '__main__':
    app.run(debug=debug, host='0.0.0.0')
