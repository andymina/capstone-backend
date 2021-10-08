#temp
from bson import ObjectId
import datetime

class Review:
  _id: ObjectId
  user_id: str
  drink_id: str
  comment: set[str] = set() #comments of drinks from this review
  date: datetime.datetime.now()

  def __init__(self, comment):
    """
    Create a Review object according to our system diagram.
    """
    self.comment = comment

  #need to come back to this funciton
  def toJSON(self) -> dict[str, str]:

    res = vars(self)

    # assure that every val is a str
    for key in res.keys():
      res[key] = str(res[key])

    return res

# sample code
# andy = User("andy", "mina", "a@gmail.com", "123")
# print(andy.toJSON())