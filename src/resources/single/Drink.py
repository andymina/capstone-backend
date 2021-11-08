from db.driver import DBdriver
from bson import ObjectId
from flask_restful import Resource, reqparse

class SingleDrink(Resource):
  """API for single drink endpoints.

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

  def __init__(self) -> None:
    self.db = DBdriver()
    self.drink_dne = {
      "data": {
        "res": None,
        "err": "Drink with that _id DNE"
      }
    }, 404
    self.parser = reqparse.RequestParser(bundle_errors = True)
    self.parser.add_argument('fields', type = dict)

  def get(self, _id: str) -> tuple[dict, int]:
    """Gets the drink with the given _id.

      Arguments:
        - _id { str } [ROUTE]: ObjectId
      
      Returns:
        - `tuple[dict, int]`: If the drink with the given _id DNE, returns None. If
          a corresponding drink is found, returns it.
    """
    # search for _id in DBdriver
    res = self.db.getDrink(ObjectId(_id))
    return self.drink_dne if not res else { "data": res.toJSON() }, 200

  def put(self, _id: str) -> tuple[dict, int]:
    """Updates the drink with the given _id.

      Arguments:
        - _id { str } [ROUTE]: ObjectId
        - fields { dict } [API]: (k, v) pairs where k represents the key to updated
          and v represents its new value. Required.
      
      Returns:
        - `tuple[dict, int]`: If fields is missing or empty, returns None. If the drink with 
        given _id DNE, returns None. Otherwise, returns the newly updated Drink.
    """
    args = self.parser.parse_args()

    # error handling
    if args["fields"] is None:
      return { "data": { "err": "Missing fields parameter." } }, 400
    elif not len(args["fields"]):
      return { "data": { "err": "Parameter 'fields' cannot be empty." } }, 400

    res = self.db.updateDrink(ObjectId(_id), args["fields"])
    return self.drink_dne if not res else { "data": res.toJSON() }, 200

  def delete(self, _id: str) -> tuple[dict, int]:
    """Deletes the drink with the given _id.

      Arguments:
        - _id { str } [ROUTE]: ObjectId
      
      Returns:
        - `tuple[dict, int]`: If drink with the _id DNE, returns None. Otherwise returns the _id
          of the deleted drink.
    """
    res = self.db.deleteDrink(ObjectId(_id))
    return self.drink_dne if not res else { "data": _id }, 200
