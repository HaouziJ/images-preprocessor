from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/image/<string:md5>")
def image(md5):
    return render_template("image.html", data=md5)


@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html", data="Images monitoring")
