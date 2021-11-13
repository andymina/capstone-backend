from bson import ObjectId
from db.driver import DBdriver
from flask_restful import Resource, reqparse

class MultipleDrink(Resource):
  """API for multiple drink endpoints.
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
    self.drink_dne = ({
      "data": {
        "res": None,
        "err": "Drink with that _id DNE"
      }
    }, 404)
    self.parser = reqparse.RequestParser(bundle_errors = True)

  def get(self) -> tuple[dict, int]:
    """Gets a list of drinks given a list of _ids. If the parameter `sample` is provided,
      returns a sample of N drinks in the database. If neiher `sample` nor `_ids` is provided,
      returns a sample of 10 drinks in the database.

      Arguments:
        - `_ids` { list[str] } [API]: list of _ids for drinks
        - `sample` { int } [API]: number of drinks to sample from the database
      
      Returns:
        - `tuple[dict, int]`: Returns a list of the corresponding drink objects. If a drink
          with the corresponding _id DNE, `None` is returned in its place. Returns an errmsg
          if _ids parameter is missing or empty.
    """
    # add args to the parser
    self.parser.add_argument("_ids", type = str, action = "append")
    self.parser.add_argument("sample", type = int)
    # grab args
    args = self.parser.parse_args()
    
    # error handling and res 
    if args["_ids"] is not None and args["sample"] is not None: # both exist
      return ({ "data": { "err": "Cannot pass both _ids and sample parameters; choose one." } }, 400)
    elif args["_ids"] is not None: # _ids but not sample
      if not len(args["_ids"]):
        return ({ "data": { "err": "Parameter `_ids` cannot be empty." } }, 400)

      res = []
      for _id in args["_ids"]:
        drink = self.db.getDrink(ObjectId(_id))
        res.append(None if drink is None else drink.toJSON())
    else: # sample may or may not exist
      sample = 9 if args["sample"] is None else args["sample"]
      res = [ drink.toJSON() for drink in self.db.sampleDrinks(sample) ]
    
    return ({ "data": res }, 200)

  def post(self) -> tuple[dict, int]:
    """Creates a Drink given the necessary data to make a drink.

      Arguments:
        - `user_email` { str } [API]: creator's email
        - `name` { str } [API]: name of the drink
        - `ingredients` { list[list[str]] } [API]: 2D array of ingredients for this drink.
          See models/Drink.py for more details.
      
      Returns:
        - `tuple[dict, int]`: Returns the newly created Drink. If the Drink exists already,
          returns the existing drink.
    """
    # grab args
    self.parser.add_argument('user_email', type = str)
    self.parser.add_argument('name', type = str)
    self.parser.add_argument('ingredients', type = list, action= "append")
    args = self.parser.parse_args()
    
    email, name, ings = params = (args['user_email'], args["name"], args["ingredients"])

    # error handling 
    if None in params:
      return ({ "data": { "err": "Missing one of ['user_email', 'name', 'ingredients']" } }, 400)
    if not len(ings):
      return ({ "data": { "err": "Parameter `ingredients` cannot be empty." } }, 400)

    res = self.db.createDrink(email, name, ings)
    return ({ "data": res.toJSON() }, 200)

  def delete(self) -> tuple[dict, int]:
    """Removes drinks from the database given a list of corresponding _ids.

      Arguments:
        - `_ids` { list[str] } [API]: list of _ids for drinks
      
      Returns:
        - `tuple[dict, int]`: Returns a list of the corresponding drink objects. If a drink
          with the corresponding _id DNE, it is ommitted from the result array.
          Returns an errmsg if _ids parameter is missing or empty.
      
      Returns:
        - `tuple[dict, int]`: [description]
    """
    # grab args
    self.parser.add_argument("_ids", type = str, action = "append")
    args = self.parser.parse_args()

    # error handling 
    if args["_ids"] is None:
      return ({ "data": { "err": "Parameter `_ids` required." } }, 400)
    elif not len(args["_ids"]):
      return ({ "data": { "err": "Parameter `_ids` cannot be empty." } }, 400)

    res = [ _id if self.db.deleteDrink(ObjectId(_id)) else None for _id in args["_ids"] ]
    return ({ "data": res }, 200)