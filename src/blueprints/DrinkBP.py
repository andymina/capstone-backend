from flask import Blueprint, request
from flask_cors import CORS
from db.driver import DBdriver
from logging import getLogger

api = Blueprint('DrinkAPI', __name__)
CORS(api)
db = DBdriver(getLogger('main'))

@api.route("/get-drink", methods = ["GET"])
def getDrink():
    return db.getDrink(request.args["_id"])