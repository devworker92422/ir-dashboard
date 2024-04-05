import os
from dotenv import load_dotenv

MONGO_ALIAS1 = os.getenv("MONGO_ALIAS1")
MONGO_ALIAS2 = os.getenv("MONGO_ALIAS2")
MONGO_ALIAS3 = os.getenv("MONGO_ALIAS3")

class Config(object):
    DEBUG = False
    TESTING = False
    MONGO_URI = os.getenv("MONGO_URI")
    SECRET_KEY = os.getenv("SECRET_KEY") or "800133ce741f959351e856a9a9ad213a"
    MONGODB_SETTINGS   = [
        {"alias": MONGO_ALIAS1, "host": os.getenv("MONGO_URI1")},
        {"alias": MONGO_ALIAS2, "host": os.getenv("MONGO_URI2")},
        {"alias": MONGO_ALIAS3, "host": os.getenv("MONGO_URI3")}
    ]
    MAIL_USE_TLS = (os.getenv("MAIL_USE_TLS"))
    MAIL_USE_SSL = (os.getenv("MAIL_USE_SSL"))
    # MAIL_PORT = int(str(os.getenv("MAIL_PORT")))
    MAIL_PORT = 587
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_USERNAME = os.getenv("MAIL_USER")
    MAIL_PASSWORD = os.getenv("MAIL_PWD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    MONGODB_SETTINGS   = [
        {"alias": MONGO_ALIAS1, "host": os.getenv("MONGO_URI1")},
        {"alias": MONGO_ALIAS2, "host": os.getenv("MONGO_URI2")},
        {"alias": MONGO_ALIAS3, "host": os.getenv("MONGO_URI3")}
    ]


class TestingConfig(Config):
    TESTING = True
