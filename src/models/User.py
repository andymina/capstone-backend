from bson import ObjectId
from pprint import pformat

class User:
  types = ['drink', 'favorite', 'review']

  def __init__(self, fname: str, lname: str, email: str, pw: str) -> None:
    """Create a User object according to our system diagram.
    """
    # set basic user info
    self.fname = fname
    self.lname = lname
    self.email = email
    self.pw = pw

    # set _id fields
    self.review_ids = set() #ObjectIds of reviews from this user
    self.drink_ids = set() #ObjectIds of drinks from this user
    self.favorite_ids = set() #ObjectIds of user's favorited drinks

  def __repr__(self) -> str:
    data = pformat(vars(self))[1:-1]
    return f"User <\n {data}\n>"

  def add_item(self, type: str, _id: ObjectId) -> None:
    """Adds the item specified to this user and updates the document representation.

      Arguments:
        - type { str }: must be one of ['drink', 'favorite', 'review'].
        - _id { ObjectId }: the ObjectId of the item to be added.
      
      Raises:
          - `ValueError`: if `type` is not one of the above.
          - `TypeError`: if `_id` is not an ObjectId.
    """
    # error checking
    if type not in self.types:
      raise ValueError(f"`type` must be one of {User.types}")
    elif not isinstance(_id, ObjectId):
      raise TypeError("`_id` must be an ObjectId")

    # grab the collection of _ids we want
    getattr(self, f"{type}_ids").add(_id)

  def remove_item(self, type: str, _id: ObjectId) -> bool:
    """Removes the specified item from this user by _id.

      Arguments:
        - type { str }: must be one of ['drink', 'favorite', 'review'].
        - _id { ObjectId }: the ObjectId of the item to be added.
      
      Raises:
          - `ValueError`: if `type` is not one of the above.
          - `TypeError`: if `_id` is not an ObjectId.

      Returns:
          - `bool`: True if the drink was removed; False otherwise.
    """
    # error checking
    if type not in self.types:
      raise ValueError(f"`type` must be one of {User.types}")
    elif not isinstance(_id, ObjectId):
      raise TypeError("`_id` must be an ObjectId")

    # remove if found
    if _id in getattr(self, f"{type}_ids"):
      getattr(self, f"{type}_ids").remove(_id)
      return True

    return False
  
  def toJSON(self) -> dict:
    """Converts this object into a JSON-compatible dict that can sent by Flask directly.

      Returns:
        - `dict`: a JSON-compatible dict of this object.
    """
    # grab the dict
    res = vars(self)

    # manually convert any non-JSON fields
    if self._id is not None:
      res['_id'] = str(self._id) 
    for s in self.types:
      res[s + '_ids'] = [str(_id) for _id in getattr(self, s + '_ids')]

    return res