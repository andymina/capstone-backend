from flask import Blueprint

api = Blueprint('ReviewAPI', __name__)

@api.route("/review")
def hello_world():
    return { "data": "Hello from ReviewAPI" }