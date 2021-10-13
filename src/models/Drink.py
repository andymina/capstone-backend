from bson import ObjectId
from pprint import pformat

class Drink:

  def __init__(self, user_id: ObjectId, ingredients = [ ]) -> None :
    self._id: ObjectId = None
    self.user_id = user_id
    self.ingredients = ingredients

  def __repr__(self) -> str:
    data = pformat(vars(self))[1:-1]
    return f"Drink<\n {data}\n>"

  def toJSON(self) -> dict:
    res = vars(self)
    res['user_id'] = str(self.user_id)

    return res