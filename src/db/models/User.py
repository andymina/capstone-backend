from bson import ObjectId

class User:
  _id: ObjectId = None
  fname: str
  lname: str
  email: str
  pw: str
  types = ['drink', 'favorite', 'review']
  review_ids: set[ObjectId] = set() #ObjectIds of reviews from this user
  drink_ids: set[ObjectId] = set() #ObjectIds of drinks from this user
  favorite_ids: set[ObjectId] = set() #ObjectIds of user's favorited drinks

  def __init__(self, fname: str, lname: str, email: str, pw: str) -> None:
    """Create a User object according to our system diagram.
    """

    self.fname = fname
    self.lname = lname
    self.email = email
    self.pw = pw

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

  def to_dict(self) -> dict:
    """Converts this object to a dictionary representation. Used to read/write
      from MongoDB.

      Returns:
          - dict
              - A dict of (key, value) pairs that can directly be uploaded
              to MongoDB
    """
    res = vars(self)

    for s in ['drink', 'favorite', 'review']:
      res[s + '_ids'] = list(getattr(self, s + '_ids'))
    
    return res
  
  def toJSON(self) -> dict:
    """Converts this object into a JSON-compatible dict that can sent
      by Flask directly.

      Returns:
          - dict
              - A JSON-compatible dict of this object.
    """
    res = vars(self)

    # manually convert any non-JSON fields
    res['_id'] = str(self._id)
    for s in ['drink', 'favorite', 'review']:
      res[s + '_ids'] = [str(_id) for _id in getattr(self, s + '_ids')]

    return res

# sample code
# andy = User("andy", "mina", "a@gmail.com", "123")
# andy.add_item('drink', ObjectId(b'foo-bar-quux'))
# print('---------- document ---------')
# print(andy.to_dict())
# print('---------- JSON ---------')
# print(andy.toJSON())