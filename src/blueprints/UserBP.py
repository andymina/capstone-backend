from logging import Logger
import logging
from flask import Blueprint
from db.driver import DBdriver
from logging import getLogger

api = Blueprint('UserAPI', __name__)
db = DBdriver(getLogger())

@api.route("/user")
def hello_world():
    return { "data": "Hello from UserAPI" }