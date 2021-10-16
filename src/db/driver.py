import os, pymongo
from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.database import Database
from models import User, Review, Drink

class DBdriver:
  def __init__(self) -> None:
    """A driver used to make writing and reading from the database easier.

      Raises:
        - `ConnectionError`: Raised if the driver failed to connect to MongoDB
    """
    client = pymongo.MongoClient(os.environ['MONGODB_URI'])

    try:
      # ping is cheap and doesn't require auth
      client.admin.command('ping')
      print('Connected to MongoDB')
    except pymongo.ConnectionFailure:
      raise ConnectionError('Failed to connect to MongoDB')
    
    # connect to the capstone database
    self.client: Database = client.capstone
    self.serializers = {
      'drink': self.toDrink,
      'review': self.toReview,
      'user': self.toUser
    }

  # region User
  def toUser(self, doc: dict) -> User:
    """Converts a MongoDB document to a User.

      Arguments:
        - doc { dict }: a document representing a User

      Returns:
        - `User`
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
        - `User` or `None`: User object if the user exists. `None` otherwise.
    """
    # query for the user
    res = self.client.users.find_one({ 'email': email })
    return self.toUser(res) if res else None

  def createUser(self, fname: str, lname: str, email: str, pw: str) -> User:
    """Creates a User in the db and returns it.

      Arguments:
        - fname { str }
        - lname { str }
        - email { str }
        - pw { str }

      Returns:
        - `User`: the newly created User. If the user already exists, returns it.
    """
    # check if this user exists and return it
    existing_user = self.getUser(email)
    if existing_user is not None:
      return existing_user

    # create a new user
    temp = User(fname, lname, email, pw)
    # grab the dict for Mongo
    doc = vars(temp).copy()
    for type in User.types:
      doc[type + '_ids'] = list(doc[type + '_ids'])
    
    # create in db and return
    temp._id = self.client.users.insert_one(doc).inserted_id
    return temp

  def attachItem(self, type: str, email: str, _id: ObjectId, hint: User = None):
    """Attach an item to the User given the user's email and item's _id.

      Arguments:
        - type { str }: Must be one of ['drink', 'favorite', 'review'].
        - email { str }
        - _id { ObjectId }
        - hint { User, optional }: Providing a User for hint will prevent getting the User
          from the database. Defaults to None.

      Raises:
         - `KeyError`: raised if User with the given email (email param or hint.email) DNE.
    """
    # grab the user
    target = hint if hint is not None else self.getUser(email)
    if target is None:
      raise KeyError(f"User with email `{target.email}` DNE")

    # attempt to update db
    res = self.client.users.update_one(
      { 'email': target.email },
      { '$addToSet': { f"{type}_ids": _id } }
    )
    # check if update failed
    if res.modified_count == 0:
      raise KeyError(f"User with email `{target.email}` DNE")

    target.add_item(type, _id)

  def detachItem(self, type: str, email: str, _id: ObjectId, hint: User = None):
    """Optimized way to detach _id from user's drinks, favorites, or reviews.

      Arguments:
        - type { str }: Must be one of ['drink', 'favorite', 'review']
        - email { str }
        - _id { ObjectId }
        - hint { User, optional }: Providing a User for hint will prevent getting the User
          from the database. Defaults to None.

      Raises:
         - `KeyError`: raised if User with the given email (email param or hint.email) DNE.
    """
    # grab the user
    target = hint if hint is not None else self.getUser(email)
    if target is None:
      raise KeyError(f"User with email `{target.email}` DNE")

    # attempt to update db
    res = self.client.users.update_one(
      { 'email': target.email },
      { '$pullAll': { f"{type}_ids": _id } }
    )
    # check if update failed
    if res.modified_count == 0:
      raise KeyError(f"User with email `{target.email}` DNE")

    target.remove_item(type, _id)

  def getItems(self, type: str, email: str) -> list:
    """Returns all items of 'type' created by this user.

      Arguments:
        - type { str }: Must be one of ['drink', 'review', 'favorite']
        - email { str }

      Raises:
        - `ValueError`: if type is not one of ['drink', 'favorite', 'review']
      
      Returns:
        - `list`: list of type objects for the given user. If type is 'favorite'
          a list of Drinks will be returned.
    """
    if type not in User.types:
      raise ValueError(f"`type` must be one of {User.types}")

    # grab ObjectIds
    qres = self.client.users.find_one({ 'email': email }, { "_id": 0, f"{type}_ids": 1 })

    if qres is None:
      raise KeyError(f"User with email {email} DNE")

    _ids = qres[f"{type}_ids"]
    # set type to align with collections
    type = 'drink' if type == 'favorite' else type
    # grab Objects
    res = []
    for item in self.client[f"{type}s"].find({ '_id': { '$in': _ids } }):
      res.append(self.serializers[type](item))
    return res

  def updateUser(self, email: str, fields: dict) -> User or None:
    """Updates the fields of User by email. If DNE, returns `None`.

      Arguments:
        - email { str }
        - fields { dict }: k, v pairs of the fields to be updated and their new values

      Returns:
        - `User`: the updated User
        - `None`: if Fields is an empty dict or User DNE.
    """
    # check we don't process any of User.types
    for type in User.types:
      if type in fields:
        raise UserWarning(
          "Use `attachItem` and `detachItem` when updating containers\
          of _ids as they are optimized for this functionality"
        )
    
    if len(fields) == 0:
      return None

    # attempt to update in db
    res = self.client.users.find_one_and_update(
      { 'email': email }, { '$set': fields },
      return_document = ReturnDocument.AFTER
    )

    return self.toUser(res) if res else None

  # endregion
  
  # region Review
  def toReview(self, doc: dict) -> Review:
    """Converts a MongoDB document to a Review.

      Arguments:
        - doc { dict }: a document representing a Review

      Returns:
          - `Review`
    """
    res = Review(
      doc['user_email'], doc['drink_id'],
      doc['comment'], doc['rating'],
      doc['date']
    )
    # set _id
    res._id = doc['_id']

    return res
  
  def getReview(self, _id: ObjectId) -> Review or None:
    """Gets a Review by _id.

      Returns:
        - `Review` or `None`: Review object if the Review exists. `None` otherwise.
    """
    res = self.client.reviews.find_one({ '_id': _id })
    return self.toReview(res) if res else None

  def createReview(self, user_email: str, drink_id: ObjectId, comment: str, rating: int) -> Review:
    """Creates a Review in the db and returns it.

      Arguments:
        - user_email { str }
        - drink_id { ObjectId }
        - comment { str }
        - rating { int }

      Returns:
        - `Review`
          - The newly created Review. If the review already exists, returns it.
    """
    existing_review = self.client.reviews.find_one({ 'user_email': user_email, 'drink_id': drink_id })
    if existing_review is not None:
      return self.toReview(existing_review)

    temp = Review(user_email, drink_id, comment, rating)
    temp._id = self.client.reviews.insert_one(vars(temp)).inserted_id
    return temp

  def updateReview(self, _id: ObjectId, fields: dict) -> Review or None:
    """Updates the fields of Review by _id. If DNE, returns `None`.

      Arguments:
        - _id { ObjectId }
        - fields { dict }: (k, v) pairs of the fields to be updated and their new values

      Returns:
        - `Review`: the updated Review.
        - `None`: if Fields is an empty dict or Review DNE.
    """
    if len(fields) == 0:
      return None

    res = self.client.reviews.find_one_and_update({ '_id': _id }, { '$set': fields })
    return self.toReview(res) if res else None

  def deleteReview(self, _id: ObjectId) -> bool:
    """Deletes a Review by _id in the db.

      Arguments:
        - _id { ObjectId }

      Returns:
          - `bool`: True if the review was removed, False otherwise.
    """
    res = self.client.reviews.delete_one({ '_id': _id })
    return bool(res.deleted_count)
  # endregion

  # region Drink
  def toDrink(self, doc: dict) -> Drink:
    """Converts a MongoDB document to a Drink.

      Arguments:
        - doc { dict }: a document representing a Drink
      
      Returns:
        - `Drink`
    """
    res = Drink(doc['user_email'], doc['name'], doc['ingredients'])
    for k, v in doc.items():
      setattr(res, k, v)
    res.review_ids = set(res.review_ids)
    return res

  def getDrink(self, _id: ObjectId) -> Drink or None:
    """Gets a Drink by _id.
      
      Returns:
        - `Drink or None`: Drink object if the Drink exists. `None` otherwise.
    """
    res = self.client.drinks.find_one({ '_id': _id })
    return self.toDrink(res) if res else None

  def createDrink(self, user_email: str, name: str, ingredients: list) -> Drink:
    """Creates a Drink in the db and returns it.

      Arguments:
        - user_email { str }
        - ingredients { list }
      
      Returns:
        - `Drink`: The newly created Drink. If the drink already exists, returns it.
    """
    existing_drink = self.getDrink({ 'user_email': user_email, 'name': name })
    if existing_drink is not None:
      return existing_drink

    # create new Drink
    temp = Drink(user_email, name, ingredients)
    doc = vars(temp).copy()
    doc['review_ids'] = list(doc['review_ids'])

    temp._id = self.client.drinks.insert_one(doc).inserted_id
    return temp
  
  def attachReview(self, drink_id: ObjectId, review_id: ObjectId, hint: Drink = None):
    """Attach a review to the drink specified by _id.

      Arguments:
        - drink_id { ObjectId }
        - review_id { ObjectId }
        - hint { Drink, optional }:Providing a User for hint will prevent getting the User
          from the database. Defaults to None.

      Raises:
        - `KeyError`: raised if User with the given email (email param or hint.email) DNE.
    """
    # grab the user
    target = hint if hint is not None else self.getDrink(drink_id)
    if target is None:
      raise KeyError(f"Drink with {drink_id} DNE")
    
    # attempt to update db
    res = self.client.drinks.update_one(
      { '_id': target._id },
      { '$addToSet': { 'review_ids': review_id } }
    )

    if res.modified_count == 0:
      raise KeyError(f"Drink with {drink_id} DNE")
    
    target.add_review(review_id)

  def detachReview(self, drink_id: ObjectId, review_id: ObjectId, hint: Drink = None):
    """Detaches the review with the associated _id from this drink.

      Arguments:
        - drink_id { ObjectId }
        - review_id: { ObjectId }
        - hint { Drink, optional }: Providing a User for hint will prevent getting the User
          from the database. Defaults to None.

      Raises:
        - `KeyError`: raised if User with the given email (email param or hint.email) DNE.
    """
    # grab the user 
    target = hint if hint is not None else self.getDrink(drink_id)
    if target is None:
      raise KeyError(f"Drink with drink_id {drink_id} DNE")

    # attempt to update db
    res = self.client.drinks.update_one(
      { '_id': target._id },
      { '$pullAll': { "review_ids": review_id } }
    )
    # check if update failed
    if res.modified_count == 0:
      raise KeyError(f"Drink with drink_id {drink_id} DNE")

    target.remove_review(review_id)

  def getReviews(self, drink_id: ObjectId) -> list[Review]:
    """Returns a list of Reviews attached to this drink.

      Arguments:
        - drink_id { ObjectId }
    """
    qres = self.client.drinks({ '_id': drink_id }, { '_id': 0, 'review_ids': 1 })

    if qres is None:
      raise KeyError(f"Drink with drink_id {drink_id} DNE")

    _ids = qres["review_ids"]
    res = []
    for item in self.client.reviews.find({ '_id': { '$in': _ids } }):
      res.append(self.toReview(item))
    
    return res

  def updateDrink(self, _id: ObjectId, fields: dict) -> Drink or None:
    """Updates the fields of Drink by _id. If DNE, returns `None`.

      Arguments:
        - _id { ObjectId }
        - fields { dict }: (k, v) pairs of the fields to be updated and their new values

      Returns:
        - `Drink`: the updated Drink.
        - `None`: if Fields is an empty dict or Drink DNE.
    """
    if len(fields) == 0:
      return None
    
    # attempt to update in db
    res = self.client.drinks.find_one_and_update(
      { '_id': _id }, { '$set': fields },
      return_document = ReturnDocument.AFTER
    )

    return self.toDrink(res) if res else None

  def deleteDrink(self, _id: ObjectId) -> bool:
    """Deletes a Drink by _id in the db.

      Arguments:
        - _id { ObjectId }

      Returns:
          - `bool`: True if the Drink was removed, False otherwise.
    """
    res = self.client.drinks.delete_one({ '_id': _id })
    return bool(res.deleted_count)

  # endregion

# region sample code
# d = DBdriver()

# user
# andy = d.createUser('andy', 'mina', 'andy@gmail.com', '123')

# endregion