from db.driver import DBdriver
from bson import ObjectId
from flask_restful import Resource, reqparse

class SingleUser(Resource):
  def __init__(self):
    self.db = DBdriver()
    self.user_dne = {
      "data": {
        "res": None,
        "err": "User with that email DNE"
      }
    }, 404
    self.parser = reqparse.RequestParser(bundle_errors = True)

  def get(self, email: str) -> tuple[dict, int]:
    # grab the user
    res = self.db.getUser(email)
    return self.user_dne if not res else { "data": res.toJSON() }, 200

  def put(self, email: str) -> tuple[dict, int]:
    # grab args
    self.parser.add_argument("fields", type = dict)
    args = self.parser.parse_args()

    # error handling
    if args["fields"] is None:
      return { "data": { "err": "Missing fields parameter." } }, 400
    elif not len(args["fields"]):
      return { "data": { "err": "Parameter 'fields' cannot be empty." } }, 400

    res = self.db.updateUser(email, args["fields"])
    return self.user_dne if not res else { "data": res.toJSON() }, 200

  def delete(self, email: str) -> tuple[dict, int]:
    res = self.db.deleteUser(email)
    return self.user_dne if not res else { "data": email }, 200