from flask import Blueprint
from db.driver import DBdriver

api = Blueprint('UserAPI', __name__)
db = DBdriver()

@api.route("/user")
def hello_world():
    return { "data": "Hello from UserAPI" }