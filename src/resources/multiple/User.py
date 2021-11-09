from db.driver import DBdriver
from flask_restful import Resource, reqparse

class MultipleUser(Resource):
  def __init__(self):
    self.db = DBdriver()
    self.user_dne = {
      "data": {
        "res": None,
        "err": "User with that email DNE."
      }
    }, 404
    self.parser = reqparse.RequestParser()

  def get(self) -> tuple[dict, int]:
    # grab args
    self.parser.add_argument("emails", type = str, action = "append")
    args = self.parser.parse_args()
    
    # error handling
    if args["emails"] is None:
      return { "data": { "err": "Parameter `emails` cannot be empty." } }, 400

    res = [ self.db.getUser(email).toJSON() for email in args["emails"] ]
    return { "data": res }, 200

  def post(self) -> tuple[dict, int]:
    # grab args
    self.parser.add_argument("fname", type = str)
    self.parser.add_argument("lname", type = str)
    self.parser.add_argument("email", type = str)
    self.parser.add_argument("pw", type = str)
    args = self.parser.parse_args()

    # error handling
    params = ["fname", "lname", "email", "pw"]
    for p in params:
      if args[p] is None:
        return { "data": { "err": f"Parameter `{p}` is required." } }, 400
      elif args[p] == "":
        return { "data": { "err": f"Parameter `{p}` cannot be empty." } }, 400

    # create the user
    res = self.db.createUser(args["fname"], args["lname"], args["email"], args["pw"])

    return { "data": res.toJSON() }, 200

  def delete(self) -> tuple[dict, int]:
    # grab args
    self.parser.add_argument("emails", type = str, action = "append")
    args = self.parser.parse_args()

    # error handling
    if args["emails"] is None:
      return { "data": { "err": "Parameter `emails` cannot be empty." } }, 400

    res = [ email for email in args["emails"] if self.db.deleteUser(email) ]
    return { "data": res }, 200