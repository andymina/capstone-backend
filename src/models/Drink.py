from bson import ObjectId
from pprint import pformat

class Drink:

  def __init__(self, user_email: str, name: str, ingredients: list) -> None:
    """Create a Drink according to our system diagram.

      Arguments:
        - user_id { ObjectId }: the _id of the user who created this Drink
        - ingredients { list }: a 2D list where each sublist contains two strings:
          the ingredient and the unit. For example: 
          `[["strawberry", "4"], ["caramel", "2 pump"]]`
    """
    self.user_email = user_email # _id of creator
    self.name = name # name of this drink
    self.review_ids = set()  # _ids of reviews
    self.ingredients = ingredients
    self.rating = -1 # set to -1 for no reviews with ratings, increments of .5
    self.sum = 0.0 # rolling sum for online avg calcs

  def __repr__(self) -> str:
    """Provides a string representation for this class.
    """
    data = pformat(vars(self))[1:-1]
    return f"Drink <\n {data}\n>"

  def add_review(self, _id: ObjectId, val: int) -> None:
    """Add a review to this drink by _id.
    """
    # error check
    if not isinstance(_id, ObjectId):
      raise TypeError("`id` must be an ObjectId")
    
    # add review
    self.review_ids.add(_id)
    # calc the new avg
    self.update_rating(val)

  def remove_review(self, _id: ObjectId, val: int) -> bool:
    """Remove a review from this drink by _id.

      Raises:
        - `TypeError`: raised is _id is not an ObjectId.

      Returns:
        - `bool`: True if the drink was removed; False otherwise.
    """
    # error check
    if not isinstance(_id, ObjectId):
      raise TypeError("`_id` must be on ObjectId")
    elif _id not in self.review_ids:
      return False

    # remove it
    self.review_ids.remove(_id)
    # calc the new avg
    self.update_rating(-val)
    return True

  def update_rating(self, val: int) -> None:
    # calc the new avg
    self.sum += val
    self.rating = 0.5 * round((self.sum / len(self.review_ids)) / 0.5)

  def toJSON(self) -> dict:
    res = vars(self)
    if res['_id'] is not None:
      res['_id'] = str(res['_id'])
    res['review_ids'] = [str(_id) for _id in self.review_ids]
    return res