from bson import ObjectId

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
    self._id: ObjectId = None
    self.review_ids = set() #ObjectIds of reviews from this user
    self.drink_ids = set() #ObjectIds of drinks from this user
    self.favorite_ids = set() #ObjectIds of user's favorited drinks

  def add_item(self, type: str, _id: ObjectId) -> None:
    """Adds the item specified to this user and updates the document representation.

      Arguments:
          - `type` { str }
              - Must be one of ['drink', 'favorite', 'review'].
          - `_id` { ObjectId }
              - The ObjectId of the item to be added.
      
      Raises:
          - `ValueError`
              - Raised if `type` is not one of the above.
          - `TypeError`
              - Raised if `_id` is not an ObjectId.
    """
    # error checking
    if type not in self.types:
      raise ValueError("`type` must be one of ['drink', 'favorite', 'review']")
    if not isinstance(_id, ObjectId):
      raise TypeError("`_id` must be an ObjectId")

    # grab the collection of _ids we want
    getattr(self, type + '_ids').add(_id)

  def remove_item(self, type: str, _id: ObjectId) -> bool:
    """Removes the specified item from this user.

      Arguments:
          - `type` { str }
              - Must be one of ['drink', 'favorite', 'review'].
          - `_id` { ObjectId }
              - The ObjectId of the item to be removed.

      Raises:
          - `ValueError`
              - Raised if `type` is not one of the above.
          - `TypeError`
              - Raised if `_id` is not an ObjectId.

      Returns:
          - bool
              - Returns True if the drink was removed; False otherwise.
    """
    # error checking
    if type not in self.types:
      raise ValueError("`type` must be one of ['drink', 'favorite', 'review']")
    if not isinstance(_id, ObjectId):
      raise TypeError("`_id` must be an ObjectId")

    # remove if found
    if _id in getattr(self, type + '_ids'):
      getattr(self, type + '_ids').remove(_id)
      return True

    return False
  
  def toJSON(self) -> dict:
    """Converts this object into a JSON-compatible dict that can sent
      by Flask directly.

      Returns:
          - dict
              - A JSON-compatible dict of this object.
    """
    # grab the dict
    res = vars(self)

    # manually convert any non-JSON fields
    if self._id is not None:
      res['_id'] = str(self._id) 
    for s in self.types:
      res[s + '_ids'] = [str(_id) for _id in getattr(self, s + '_ids')]

    return res

# sample code
andy = User("andy", "mina", "a@gmail.com", "123")
andy.add_item('drink', ObjectId(b'foo-bar-quux'))
print('---------- document ---------')
print(vars(andy))
print('---------- JSON ---------')
print(andy.toJSON())