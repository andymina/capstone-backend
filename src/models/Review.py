from bson import ObjectId
from pprint import pformat
import datetime

class Review:

  def __init__(self, user_id: ObjectId, drink_id: ObjectId, comment: str, rating: int) -> None:
    """
    Create a Review object according to our system diagram.
    """
    self._id: ObjectId = None
    self.user_id = user_id
    self.drink_id = drink_id
    self.comment = comment
    self.rating = rating
    self.date = datetime.datetime.now()

  def __repr__(self) -> str:
    data = pformat(vars(self))[1:-1]
    return f"Review <\n {data}\n>"

  #need to come back to this funciton
  def toJSON(self) -> dict:
    res = vars(self)
    # convert _id fields and date
    if self._id is not None:
      res['_id'] = str(self._id) 
    res['user_id'] = str(self.user_id)
    res['drink_id'] = str(self.drink_id)
    res['date'] = str(self.date)

    return res