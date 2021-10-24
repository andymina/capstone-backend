from flask import Blueprint, request
from flask_cors import CORS
from db.driver import DBdriver
from logging import getLogger

api = Blueprint('ReviewAPI', __name__)
CORS(api)
db = DBdriver(getLogger('main'))

@api.route("/review")
def hello_world():
    return { "data": "Hello from ReviewAPI" }