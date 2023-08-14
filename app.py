# Standard library imports
import os
import dotenv
import threading

# Third party imports
import flask
import flask_cors


# Local application imports
import blueprint_ID as bp_ID

# import blueprints.blueprint_geode as bp_geode

if os.path.isfile("./.env"):
    basedir = os.path.abspath(os.path.dirname(__file__))
    dotenv.load_dotenv(os.path.join(basedir, ".env"))

""" Global config """
app = flask.Flask(__name__)


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.daemon = True
    t.start()
    return t


def kill():
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    if len(os.listdir(LOCK_FOLDER)) == 0:
        os._exit(0)
    if os.path.isfile(LOCK_FOLDER + "/ping.txt"):
        os.remove(LOCK_FOLDER + "/ping.txt")


""" Config variables """
FLASK_DEBUG = True if os.environ.get("FLASK_DEBUG", default=None) == "True" else False


PORT = int(app.config.get("PORT"))
CORS_HEADERS = app.config.get("CORS_HEADERS")
UPLOAD_FOLDER = app.config.get("UPLOAD_FOLDER")
LOCK_FOLDER = app.config.get("LOCK_FOLDER")
ORIGINS = app.config.get("ORIGINS")
SSL = app.config.get("SSL")


app.register_blueprint(bp_ID.ID_routes, url_prefix=f"/{ID}", name="ID_blueprint")
app.register_blueprint(
    bp_geode.geode_routes, url_prefix=f"/{ID}/tools", name="geode_blueprint"
)


if FLASK_DEBUG == False:
    app.config.from_object("config.ProdConfig")
    set_interval(kill, 150)
else:
    app.config.from_object("config.DevConfig")
flask_cors.CORS(app, origins=ORIGINS)


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = flask.json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


@geode_routes.route("/sharetwin/createbackend", methods=["POST", "OPTIONS"])
def createbackend():
    return flask.make_response({"ID": str("123456")}, 200)


# ''' Main '''
if __name__ == "__main__":
    print("Python is running in " + str(FLASK_DEBUG) + " mode")
    app.run(host="0.0.0.0", port=PORT, ssl_context=SSL)
