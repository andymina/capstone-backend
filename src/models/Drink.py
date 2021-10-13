from bson import ObjectId

class Drink:

  def __init__(self, user_id: ObjectId, ingredients: str) -> None :
    self._id: ObjectId
    self.user_id = user_id
    self.ingredients = ingredients


  def toJSON(self) -> dict:
    res = vars(self)
    res['user_id'] = str(self.user_id)

    # assure that every val is a str
    for key in res.keys():
      res[key] = str(res[key])

    return res