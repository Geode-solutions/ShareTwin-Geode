# Standard library imports
import os
import dotenv
import threading

# Third party imports
import flask
import flask_cors
from werkzeug.exceptions import HTTPException


# Local application imports
from blueprints import blueprint_ID
from blueprints import blueprint_share_twin

if os.path.isfile("./.env"):
    basedir = os.path.abspath(os.path.dirname(__file__))
    dotenv.load_dotenv(os.path.join(basedir, ".env"))

""" Global config """
app = flask.Flask(__name__)


def kill():
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    if len(os.listdir(LOCK_FOLDER)) == 0:
        os._exit(0)
    if os.path.isfile(LOCK_FOLDER + "/ping.txt"):
        os.remove(LOCK_FOLDER + "/ping.txt")


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.daemon = True
    t.start()
    return t


""" Config variables """
FLASK_DEBUG = True if os.environ.get("FLASK_DEBUG", default=None) == "True" else False


if FLASK_DEBUG == False:
    print("DEBUG FALSE")
    app.config.from_object("config.ProdConfig")
    set_interval(kill, 150)
else:
    print("DEBUG TRUE")
    app.config.from_object("config.DevConfig")


PORT = app.config.get("PORT")
CORS_HEADERS = app.config.get("CORS_HEADERS")
UPLOAD_FOLDER = os.path.abspath(app.config.get("UPLOAD_FOLDER"))
LOCK_FOLDER = os.path.abspath(app.config.get("LOCK_FOLDER"))
ORIGINS = app.config.get("ORIGINS")
SSL = app.config.get("SSL")

flask_cors.CORS(app, origins=ORIGINS)


app.register_blueprint(blueprint_ID.ID_routes, name="blueprint_ID")
app.register_blueprint(
    blueprint_share_twin.share_twin_routes,
    url_prefix="/share_twin",
    name="blueprint_share_twin",
)


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


# ''' Main '''
if __name__ == "__main__":
    print("Python is running in " + str(FLASK_DEBUG) + " mode")
    app.run(host="0.0.0.0", port=PORT, ssl_context=SSL)
