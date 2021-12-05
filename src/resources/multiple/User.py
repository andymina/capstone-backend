from db.driver import DBdriver
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, create_access_token
from datetime import timedelta as delta
from os import environ
from ..validator import validate
import bcrypt

class MultipleUser(Resource):
  """API for multiple User endpoints.
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
        "err": "User with that email DNE."
      }
    }, 404)
    self.parser = reqparse.RequestParser()

  def get(self) -> tuple[dict, int]:
    """Gets a list of Users given a list of emails.

      Arguments:
        - `emails` { list[str] } [API]: list of emails for Users
      
      Returns:
        - `tuple[dict, int]`: Returns a list of the corresponding User objects. If a user
          with the corresponding _id DNE, `None` is returned in its place. Returns an errmsg
          if emails parameter is missing or empty.
    """
    # grab args
    self.parser.add_argument("emails", type = str, action = "append")
    args = self.parser.parse_args()
    
    # error handling
    if args["emails"] is None:
      return ({ "data": { "err": "Parameter `emails` cannot be empty." } }, 400)

    res = []
    for email in args["emails"]:
      user = self.db.getUser(email)
      res.append(None if user is None else user.toJSON())
    return ({ "data": res }, 200)

  def post(self) -> tuple[dict, int]:
    """Creates a User given the necessary data to make a drink. Analogous to signing up.
      Arguments:
        - `fname` { str } [API]: first name
        - `lname` { str } [API]: last name
        - `email` { str } [API]: email
        - `pw` { str } [API]: password
      
      Returns:
        - `tuple[dict, int]`: If the form is incorrect, returns the errors. Otherwise, returns a
        dict containing the token and the user.
    """
    # grab args
    self.parser.add_argument("fname", type = str)
    self.parser.add_argument("lname", type = str)
    self.parser.add_argument("email", type = str)
    self.parser.add_argument("pw", type = str)
    args = self.parser.parse_args()

    # error handling
    errors = validate(args, mode="signup")
    if len(errors) != 0:
      return ({ "data": errors }, 400)

    # hash pw and create user
    hashed = bcrypt.hashpw(args["pw"].encode("utf-8"), bcrypt.gensalt())
    hashed = hashed.decode("utf-8")
    res = self.db.createUser(args["fname"], args["lname"], args["email"], hashed)

    # create token
    token = create_access_token(res.toJSON(), expires_delta=delta(hours=12))
    return ({ "data": { "token": token, "user": res.toJSON() } }, 201)

  def delete(self) -> tuple[dict, int]:
    """Removes Users from the database given a list of corresponding emails.
      Arguments:
        - `emails` { list[str] } [API]: list of emails for Users
      
      Returns:
        - `tuple[dict, int]`: Returns a list of the corresponding Users objects. If a Users
          with the corresponding email DNE, it is ommitted from the result array.
          Returns an errmsg if emails parameter is missing or empty.
    """
    # grab args
    self.parser.add_argument("emails", type = str, action = "append")
    args = self.parser.parse_args()

    # error handling
    if args["emails"] is None:
      return ({ "data": { "err": "Parameter `emails` cannot be empty." } }, 400)

    res = [ email if self.db.deleteUser(email) else None for email in args["emails"] ]
    return ({ "data": res }, 200)