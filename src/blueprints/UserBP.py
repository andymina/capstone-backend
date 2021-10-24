from flask import Blueprint
from flask_cors.decorator import cross_origin
from db.driver import DBdriver
from logging import getLogger

api = Blueprint('UserAPI', __name__)
db = DBdriver(getLogger())

@api.route("/user")
@cross_origin
def hello_world():
    return { "data": "Hello from UserAPI" }