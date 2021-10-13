import os, pymongo
from bson import ObjectId
from dotenv import load_dotenv
from pymongo.database import Database
from models import User, Review

msg = '.env loaded' if load_dotenv() else 'Failed to load .env'
print(msg)

class DBdriver:
  client: Database

  def __init__(self) -> None:
    """A driver used to make writing and reading from the database easier.

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

  # region User
  def toUser(self, doc: dict) -> User:
    """Converts a MongoDB document to a User.

        Arguments:
            - `doc` { dict }
                - A document representing a User

        Returns:
            - User
    """
    # create the obj
    res = User(doc['fname'], doc['lname'], doc['email'], doc['pw'])
    # set User _id
    res._id = doc['_id']
    # set the containers of _ids
    for type in User.types:
      setattr(res, type + '_ids', set(doc[type + '_ids']))

    return res

  def getUser(self, email: str) -> User or None:
    """Gets a User by email.

        Returns:
            - User or `None`
                - User object if the user exists. `None` otherwise.
    """
    # query for the user
    res = self.client.users.find_one({ 'email': email })
    return self.toUser(res) if res else None

  def createUser(self, fname: str, lname: str, email: str, pw: str) -> User:
    """Creates a User in the db and returns it.

        Arguments:
            - `fname` { str }
            - `lname` { str }
            - `email` { str }
            - `pw` { str }

        Returns:
            - User
                - The newly created User. If the user already exists, returns it.
    """
    # check if this user exists and return it
    existing_user = self.getUser(email)
    if existing_user is not None:
      return existing_user

    # insert a new user
    temp = User(fname, lname, email, pw)
    temp._id = self.client.users.insert_one(vars(temp))
    return temp

  def updateUser(self, email: str, fields: dict) -> User or None:
    """Updates the fields of User by email. If DNE, returns `None`.

        Arguments:
            - `email` { str }
            - `fields` { dict }
                - k, v pairs of the fields to be updated and their new values

        Returns:
            - User
                - the updated User
            - `None`
                - if Fields is an empty dict or User DNE.
    """
    if len(fields) == 0:
      return None

    # upsert
    res = self.client.users.find_one_and_update({ 'email': email }, { '$set': fields })
    return self.toUser(res) if res else None
  # endregion
  
  # region Review
  def toReview(self, doc: dict) -> Review:
    """Converts a MongoDB document to a Review.

        Arguments:
            - `doc` { dict }
                - A document representing a Review

        Returns:
            - Review
    """
    res = Review(
      doc['user_id'], doc['drink_id'],
      doc['comment'], doc['rating'],
      doc['date']
    )
    # set _id
    res._id = doc['_id']

    return res
  
  def getReview(self, _id: ObjectId) -> Review or None:
    """Gets a Review by email.

    Returns:
        - Review or `None`
            - Review object if the Review exists. `None` otherwise.
    """
    res = self.client.reviews.find_one({ '_id': _id })
    return self.toReview(res) if res else None

  def createReview(self, user_id: ObjectId, drink_id: ObjectId, comment: str, rating: int):
    """Creates a Review in the db and returns it.

        Arguments:
            - `user_id` { ObjectId }
            - `drink_id` { ObjectId }
            - `comment` { str }
            - `rating` { int }

        Returns:
            - Review
                - The newly created Review. If the review already exists, returns it.
    """
    existing_review = self.client.reviews.find_one({ 'user_id': user_id, 'drink_id': drink_id })
    if existing_review is not None:
      return self.toReview(existing_review)

    temp = Review(user_id, drink_id, comment, rating)
    temp._id = self.client.reviews.insert_one(vars(temp))
    return temp

  def updateReview(self, _id: ObjectId, fields: dict) -> Review or None:
    """Updates the fields of Review by _id. If DNE, returns `None`.

        Arguments:
            - `_id` { ObjectId }
            - `fields` { dict }
                - k, v pairs of the fields to be updated and their new values

        Returns:
            - Review
                - the updated Review
            - `None`
                - if Fields is an empty dict or Review DNE.
    """
    if len(fields) == 0:
      return None

    res = self.client.reviews.find_one_and_update({ '_id': _id }, { '$set': fields })
    return self.toReview(res) if res else None

  def deleteReview(self, _id: ObjectId) -> bool:
    """Deletes a Review by _id in the db.

        Arguments:
            - `_id` { ObjectId }

        Returns:
            - bool
                - True if the review was removed, false otherwise.
    """
    res = self.client.reviews.delete_one({ '_id': _id })
    return res.deleted_count
  # endregion

# sample code
# d = DBdriver()
# d.createUser('andy', 'mina', 'andy@gmail.com', '123')
# andy = d.getUser('andy@gmail.com')
# print(andy)
# d.upsertUser('andy@gmail.com', { 'pw': 'abc' })