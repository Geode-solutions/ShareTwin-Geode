# Standard library imports
import os
import shutil

# Third party imports
import flask
import flask_cors

ID_routes = flask.Blueprint("blueprint_ID", __name__)
flask_cors.CORS(ID_routes)


@ID_routes.route("/", methods=["GET"])
def root():
    return flask.make_response({"message": "root"}, 200)


@ID_routes.route("/healthcheck", methods=["GET"])
def healthcheck():
    return flask.make_response({"message": "healthy"}, 200)


@ID_routes.route("/ping", methods=["POST"])
def ping():
    LOCK_FOLDER = flask.current_app.config["LOCK_FOLDER"]
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    if not os.path.isfile(LOCK_FOLDER + "/ping.txt"):
        f = open(LOCK_FOLDER + "/ping.txt", "a")
        f.close()
    return flask.make_response({"message": "Flask server is running"}, 200)


@ID_routes.route("/sharetwin/createbackend", methods=["POST", "OPTIONS"])
def create_backend():
    return flask.make_response({"ID": str("123456")}, 200)


@ID_routes.route("/delete_all_files", methods=["DELETE"])
def delete_all_files():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
    for filename in os.listdir(UPLOAD_FOLDER):
        f = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(f):
            print(f)
            os.remove(f)
        else:
            shutil.rmtree(f)

    return flask.make_response({}, 204)
