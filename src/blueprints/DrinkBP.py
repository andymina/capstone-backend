from flask import Blueprint, request
from db.driver import DBdriver
from logging import getLogger

api = Blueprint('DrinkAPI', __name__)
db = DBdriver(getLogger())

@api.route("/get-drink", methods = ["GET"])
def getDrink():
    return db.getDrink(request.args["_id"])