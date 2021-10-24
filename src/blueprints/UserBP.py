from flask import Blueprint, request
from flask_cors import CORS
from db.driver import DBdriver
from logging import getLogger

api = Blueprint('UserAPI', __name__)
CORS(api)
db = DBdriver(getLogger('main'))

@api.route("/user")
def hello_world():
    return { "data": "Hello from UserAPI" }