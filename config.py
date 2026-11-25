import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    DATABASE = os.environ.get("DATABASE", os.path.join(BASE_DIR, "portal.sqlite"))
