from bson import ObjectId
from pprint import pformat
from datetime import datetime

class Review:

  def __init__(
    self, user_email: str, drink_id: ObjectId,
    comment: str, rating: int, date = datetime.now(),
    img: str
  ) -> None:
    """Create a Review object according to our system diagram.
    """
    self.user_email = user_email
    self.drink_id = drink_id
    self.comment = comment
    self.rating = rating
    self.date = date
    self.img = img

  def __repr__(self) -> str:
    data = pformat(vars(self))[1:-1]
    return f"Review <\n {data}\n>"

  #need to come back to this funciton
  def toJSON(self) -> dict:
    res = vars(self)
    # convert _id fields and date
    if self._id is not None:
      res['_id'] = str(self._id)
    res['drink_id'] = str(self.drink_id)
    res['date'] = str(self.date)

    return res