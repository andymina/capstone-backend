#temp
from bson import ObjectId
from pprint import pformat
import datetime

class Review:
  _id: ObjectId
  user_id: str
  drink_id: str
  comment: str # make the comment to be one singualr string
  rating : str
  date = datetime.datetime.now()

  def __init__(self, user_id: str, drink_id: str, comment: str, rating: str) -> None:
    """
    Create a Review object according to our system diagram.
    """
    self.user_id = user_id
    self.drink_id = drink_id
    self.comment = comment
    self.rating = rating

    def __repr__(self) -> str:
      data = pformat(vars(self))[1:-1]
      return f"Review <\n {data}\n>"

  #need to come back to this funciton
  def toJSON(self) -> dict[str, str]:

    res = vars(self)
    res['user_id'] = str(self.user_id)
    res['drink_id'] = str(self.drink_id)
    res['date'] = self.date

    # assure that every val is a str
    for key in res.keys():
      res[key] = str(res[key])

    return res

# sample code
# andy = User("andy", "mina", "a@gmail.com", "123")
# print(andy.toJSON())