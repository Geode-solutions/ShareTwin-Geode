""" Flask configuration """
import os


class Config(object):
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", default=False)
    PORT = "5000"
    CORS_HEADERS = "Content-Type"
    UPLOAD_FOLDER = os.path.abspath("/data/")
    LOCK_FOLDER = os.path.abspath("./lock/")


class ProdConfig(Config):
    SSL = None
    ORIGINS = ["https://share-twin.com", "https://next.share-twin.com"]


class DevConfig(Config):
    SSL = None
    ORIGINS = "http://localhost:3000"
