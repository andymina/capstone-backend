import os, pymongo
from dotenv import load_dotenv
from pymongo.database import Database
from db.models.User import User
#debug
from pprint import pprint

msg = '.env loaded' if load_dotenv() else 'Failed to load .env'
print(msg)

class DBdriver:
  client: Database

  def __init__(self) -> None:
    """
    A driver used to make writing and reading from the database
    easier.

    Raises:
        - `ConnectionError`
             - Raised if the driver failed to connect to MongoDB
    """
    client = pymongo.MongoClient(os.environ['MONGODB_URI'])

    try:
      # ping is cheap and doesn't require auth
      client.admin.command('ping')
      print('Connected to MongoDB')
    except pymongo.ConnectionFailure:
      raise ConnectionError('Failed to connect to MongoDB')
    
    # connect to the capstone database
    self.client = client.capstone

  def toUser(self, doc: dict) -> User:
    # create the obj
    res = User(doc['fname'], doc['lname'], doc['email'], doc['pw'])
    # set User _id
    res._id = doc['_id']
    # set the containers of _ids
    for type in User.types:
      setattr(res, type + '_ids', set(doc[type + '_ids']))

    return res

  def getUser(self, email: str) -> User or None:
    # query for the user
    res = self.client.users.find_one({ 'email': email })
    return res if res is None else self.toUser(res)

  def createUser(self, fname: str, lname: str, email: str, pw: str) -> User:
    # check if this user exists and return it
    existing_user = self.getUser(email)
    if existing_user is not None:
      return existing_user

    # insert a new user
    temp = User(fname, lname, email, pw)
    temp._id = self.client.users.insert_one(vars(temp))
    return temp


# d = DBdriver()
# d.createUser('andy', 'mina', 'andy@gmail.com', '123')
# andy = d.getUser('andy@gmail.com')
# print(andy)