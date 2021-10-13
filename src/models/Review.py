#temp
from bson import ObjectId
from pprint import pformat
import datetime

class Review:

  def __init__(self, user_id: str, drink_id: str, comment: str, rating: int) -> None:
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
    res['user_id'] = str(self.user_id)
    res['drink_id'] = str(self.drink_id)
    res['date'] = str(self.date)

    return res

# sample code
# andy = User("andy", "mina", "a@gmail.com", "123")
# print(andy.toJSON())