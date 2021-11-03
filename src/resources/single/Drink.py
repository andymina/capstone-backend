from db.driver import DBdriver
from bson import ObjectId
from flask_restful import Resource, reqparse

class SingleDrink(Resource):
  def __init__(self) -> None:
    self.db = DBdriver()
    self.drink_dne = { "data": { "res": None, "err": "Drink with that _id DNE" } }, 404
    self.parser = reqparse.RequestParser(bundle_errors = True)
    self.parser.add_argument(
      'fields',
      type = dict,
      help = "Missing fields parameter."
    )

  def get(self, _id: str) -> tuple[dict, int]:
    # search for _id in DBdriver
    res = self.db.getDrink(ObjectId(_id))
    return self.drink_dne if not res else { "data": res.toJSON() }, 200

  def put(self, _id: str) -> tuple[dict, int]:
    args = self.parser.parse_args()

    # error handling
    if args["fields"] is None:
      return { "data": { "err": "Missing fields parameter." } }
    elif not len(args["fields"]):
      return { "data": { "err": "Parameter 'fields' cannot be empty." } }

    res = self.db.updateDrink(ObjectId(_id), args["fields"])
    return self.drink_dne if not res else { "data": res.toJSON() }, 200

  def delete(self, _id: str) -> tuple[dict, int]:
    res = self.db.deleteDrink(ObjectId(_id))
    return self.drink_dne if not res else { "data": res }, 200
