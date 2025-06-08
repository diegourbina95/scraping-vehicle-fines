from flask import Flask

import logging
from logging.handlers import RotatingFileHandler
app = Flask(__name__)
app.secret_key = "secret key"

logging.basicConfig(
        handlers=[RotatingFileHandler('./logs/iv_log.log', maxBytes=10000000, backupCount=10)],
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S')