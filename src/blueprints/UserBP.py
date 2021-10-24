from flask import Blueprint
from flask_cors import CORS, cross_origin
from db.driver import DBdriver
from logging import getLogger

api = Blueprint('UserAPI', __name__)
CORS(api)
db = DBdriver(getLogger(__name__))

@api.route("/user")
def hello_world():
    return { "data": "Hello from UserAPI" }