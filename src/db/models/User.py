class User:
  _id: str
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
    self.review_ids = set()
    self.drink_ids = set()

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