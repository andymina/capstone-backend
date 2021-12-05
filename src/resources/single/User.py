from flask_jwt_extended.utils import create_access_token
from db.driver import DBdriver
from flask_restful import Resource, reqparse
from datetime import timedelta as delta
from bson import ObjectId
import bcrypt
from ..validator import validate

class SingleUser(Resource):
  """API for single user endpoints.
    All routes return a JSON object and an HTTP status code. This is represented by a tuple where
    the first element is a JSON-compatible dict and the second element is an integer.
    
    Returns for each route are broken into two categories: potential JSON and status codes.
    All returns have a `data` key where the value is either specified or an object containing
    the specified data.
    If there is an error in execution, returns a JSON object with the following structure:
    ```
    {
      "data": {
        "res": as specified,
        "err": error message
      }
    }
    ```
    For more information on routes and returns see README.md.
  """

  def __init__(self):
    self.db = DBdriver()
    self.user_dne = ({
      "data": {
        "res": None,
        "err": "User with that email DNE"
      }
    }, 404)
    self.parser = reqparse.RequestParser(bundle_errors = True)

  def get(self, email: str) -> tuple[dict, int]:
    """Gets the user with the given _id.
      Arguments:
        - email { str } [ROUTE]: email of the user to be retrieved
      
      Returns:
        - `tuple[dict, int]`: If the user with the given email DNE, returns None. If
          a corresponding user is found, returns it.
    """
    # grab the user
    res = self.db.getUser(email)
    return self.user_dne if res is None else ({ "data": res.toJSON() }, 200)

  def post(self, email: str) -> tuple[dict, int]:
    """Logs the user in. API route = "/users/login"

      Arguments:
        - email { str }: Necessary for Flask, but not actually needed.
      
      Returns:
        - `tuple[dict, int]`: If the user with the given email DNE, returns None. If the form is
        incorrect, returns the errors. Otherwise, returns a dict containing the token and the user.
    """
    # grab args
    self.parser.add_argument("email", type = str)
    self.parser.add_argument("pw", type = str)
    args = self.parser.parse_args()

    # error handling
    errors = validate(args, mode="login")
    if len(errors) != 0:
      return ({ "data": errors }, 400)

    # grab the existing user
    user = self.db.getUser(args["email"])
    if user is None:
      return self.user_dne
    
    # check pw and create token
    pw_match = bcrypt.checkpw(args["pw"].encode("utf-8"), user.pw.encode("utf-8"))

    if not pw_match:
      return ({ "data": { "pw": "Password incorrect" } }, 401)

    token = create_access_token(user.toJSON(), expires_delta=delta(hours=12))
    return ({ "data": { "token": token, "user": user.toJSON() } }, 200)
    
  def put(self, email: str) -> tuple[dict, int]:
    """Updates the user with the given email.
      Arguments:
        - email { str } [ROUTE]
        - fields { dict } [API]: (k, v) pairs where k represents the key to updated
          and v represents its new value. Required.
      
      Returns:
        - `tuple[dict, int]`: If fields is missing or empty, returns None. If the user with 
        given email DNE, returns None. Otherwise, returns the newly updated user.
    """
    # grab args
    self.parser.add_argument("fields", type = dict)
    args = self.parser.parse_args()

    # error handling
    if args["fields"] is None:
      return { "data": { "err": "Missing fields parameter." } }, 400
    elif not len(args["fields"]):
      return { "data": { "err": "Parameter 'fields' cannot be empty." } }, 400

    # if we're updating _ids make sure to cast
    for key, val in args["fields"].items():
      if "_ids" in key:
        val = [ObjectId(_id) for _id in val] 
        args["fields"][key] = val

    res = self.db.updateUser(email, args["fields"])
    return self.user_dne if not res else ({ "data": res.toJSON() }, 200)

  def delete(self, email: str) -> tuple[dict, int]:
    """Deletes the user with the given email.
      Arguments:
        - email { str } [ROUTE]
      
      Returns:
        - `tuple[dict, int]`: If user with the email DNE, returns None.
          Otherwise returns the email of the deleted user.
    """
    deleted = self.db.deleteUser(email)
    return self.user_dne if not deleted else ({ "data": email }, 200)