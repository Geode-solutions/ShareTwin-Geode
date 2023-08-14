import os

import flask
import flask_cors

blueprint_ID = flask.Blueprint("blueprint_ID", __name__)
flask_cors.CORS(blueprint_ID)


@blueprint_ID.route("/", methods=["GET"])
def root():
    return flask.make_response({"message": "root"}, 200)


@blueprint_ID.route("/healthcheck", methods=["GET"])
def root():
    return flask.make_response({"message": "healthy"}, 200)


@blueprint_ID.route("/ping", methods=["POST"])
def ping():
    LOCK_FOLDER = flask.current_app.config["LOCK_FOLDER"]
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    if not os.path.isfile(LOCK_FOLDER + "/ping.txt"):
        f = open(LOCK_FOLDER + "/ping.txt", "a")
        f.close()
    return flask.make_response({"message": "Flask server is running"}, 200)
