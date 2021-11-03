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
    return self.error_response if not res else { "data": res.toJSON() }, 200

  def put(self, _id: str) -> tuple[dict, int]:
    args = self.parser.parse_args()
    if not args["fields"]:
      return { "data": { "err": "Missing fields parameter." } }
    res = self.db.updateDrink(ObjectId(_id), args["fields"])
    return self.error_response if not res else { "data": res.toJSON() }, 200

  def delete(self, _id: str) -> tuple[dict, int]:
    args = self.parser.parse_args()
    res = self.db.deleteDrink(ObjectId(_id))
    return self.error_response if not res else { "data": res }, 200
