from bson import ObjectId

class User:
  _id: ObjectId
  fname: str
  lname: str
  email: str
  pw: str
  review_ids: set[str] = set() #ObjectIds of reviews from this user
  drink_ids: set[str] = set() #ObjectIds of drinks from this user

  def __init__(self, fname: str, lname: str, email: str, pw: str) -> None:
    """
    Create a User object according to our system diagram.
    """
    self.fname = fname
    self.lname = lname
    self.email = email
    self.pw = pw

  def add_item(self, type: str, _id: ObjectId) -> None:
    """
    Adds the item specified to this user.

    Arguments:
        - `type` { str }
            - Can be `drink` or `review`.
        - `_id` { ObjectId }
            - The ObjectId of the item to be added
    """
    self[type].add(str(_id))

  def remove_item(self, type: str, _id: ObjectId) -> bool:
    """
    Removes the specified item from this user.

    Arguments:
        - `type` { str }
            - Can be `drink` or `review`.
        - `_id` { ObjectId }
            - The ObjectId of the item to be removed.

    Returns:
        - bool
            - Returns True if the drink was removed; False otherwise.
    """
    if str(_id) not in self[type]:
      return False
    
    self[type].remove(str(_id))
    return True

  def toJSON(self) -> dict[str, str]:
    """
    Serializes this object to JSON to better interact with our front-end.

    Returns:
        - dict[str, str]: A JSON serializable dict that can be sent
        directly through Flask.
    """
    res = vars(self)

    # assure that every val is a str
    for key in res.keys():
      res[key] = str(res[key])
    
    return res

# sample code
# andy = User("andy", "mina", "a@gmail.com", "123")
# print(andy.toJSON())