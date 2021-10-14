from bson import ObjectId
from pprint import pformat

class Drink:
  types = [-1, 0, 1, 2, 3, 4, 5]

  def __init__(self, user_id: ObjectId, ingredients = [ ]) -> None :
    self.user_id = user_id
    self.ingredients = ingredients

    # set _id fields
    self._id: ObjectId = None
    self.review_ids = set()  #ObjectIds of reviews on this drink

  def __repr__(self) -> str:
    data = pformat(vars(self))[1:-1]
    return f"Drink <\n {data}\n>"

  def add_review(self, type: int, _id: ObjectId)->None:
    # error check
    if type not in self.types:
      raise ValueError("`type` must be one of [-1, 0, 1, 2, 3, 4, 5]")
    if not isinstance(_id, ObjectId):
      raise TypeError("`id` must be an ObjectId")

    #get collections of _ids we want
    getattr(self, type + '_ids').add(_id)

  def remove_review(self, type: int, _id: ObjectId) -> bool:
    if type not in self.types:
      raise ValueError("`type` must be one of [-1, 1, 2, 3, 4, 5]")
    if not isinstance(_id, ObjectId):
      raise TypeError("`_id` must be on ObjectId")

    #remove if found
    if _id in getattr(self, type + '_ids'):
      getattr(self, type + '_ids').remove(_id)
      return True
    return False

  def toJSON(self) -> dict:
    res = vars(self)
    res['user_id'] = str(self.user_id)

    return res