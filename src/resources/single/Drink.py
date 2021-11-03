from typing_extensions import Required
from bson import ObjectId
from db.driver import DBdriver
from flask_restful import Resource, reqparse

class SingleDrink(Resource):
  def __init__(self) -> None:
    self.db = DBdriver()
    self.error_response = { "data": { "res": None, "err": "Drink with that _id DNE" } }, 404
    self.parser = reqparse.RequestParser(bundle_errors = True)
    self.parser.add_argument(
      'fields',
      type = dict,
      help = "Missing fields parameter."
    )

  def get(self, _id: str) -> tuple[dict, int]:
    # search for _id in DBdriver
    res = self.db.getDrink(ObjectId(_id))
    return { "data": res }, 200 if res else self.error_response

  def put(self, _id: str) -> tuple[dict, int]:
    args = self.parser.parse_args()
    res = self.db.updateDrink(ObjectId(_id), args['fields'])
    return { "data": res }, 200 if res else self.error_response

  def delete(self, _id: str) -> tuple[dict, int]:
    args = self.parser.parse_args()
    res = self.db.deleteDrink(ObjectId(_id))
    return { "data": _id }, 200 if res else self.error_response
