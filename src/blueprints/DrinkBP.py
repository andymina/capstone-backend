from flask import Blueprint

api = Blueprint('DrinkAPI', __name__)

@api.route("/drink")
def hello_world():
    return { "data": "Hello from DrinkAPI" }