from os import environ
from bson import ObjectId
from pymongo import ReturnDocument, MongoClient
from pymongo.database import Database
from models import User, Review, Drink
from logging import getLogger
import __main__

class DBdriver:
  def __init__(self) -> None:
    """A driver used to make writing and reading from the database easier.

      Raises:
        - `ConnectionError`: Raised if the driver failed to connect to MongoDB
    """
    mongo = MongoClient(environ['MONGODB_URI'])
    logger = getLogger(__main__.__name__)

    try:
      # ping is cheap and doesn't require auth
      mongo.admin.command('ping')
      logger.info('Connected to MongoDB')
    except:
      raise ConnectionError('Failed to connect to MongoDB')
    
    # connect to the capstone database
    self.client: Database = mongo.capstone
    self.mongo = mongo
    self.serializers = {
      'drink': self.toDrink,
      'review': self.toReview,
      'user': self.toUser
    }
    
  # region User

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
    if existing_user:
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

  def getItems(self, type: str, email: str) -> list:
    """Returns all items of 'type' created by this user.

      Arguments:
        - type { str }: Must be one of ['drink', 'review', 'favorite', 'img']
        - email { str }

      Raises:
        - `ValueError`: if type is not one of ['drink', 'favorite', 'review', 'img']
      
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

  def deleteUser(self, email: str) -> bool:
    """Deletes a user from the database.

      Arguments:
        - email { str }: the email of the User to be deleted
      
      Returns:
        - `bool`: True if the user was deleted, False otherwise.
    """
    res = self.client.users.find_one_and_delete({ "email": email })
    return bool(res)
    
  # endregion
  
  # region Review
  
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
    # check if the review exists
    existing_review = self.client.reviews.find_one({ 'user_email': user_email, 'drink_id': drink_id })
    if existing_review:
      return self.toReview(existing_review)

    # create the Review in the DB
    temp = Review(user_email, drink_id, comment, rating)
    temp._id = self.client.reviews.insert_one(vars(temp)).inserted_id

    # attach it to a drink
    self.attachReview(drink_id, temp._id, rating)
    self.attachItem('review', user_email, temp._id)
    return temp

  def updateReview(self, _id: ObjectId, fields: dict) -> Review or tuple[Review, int]:
    if len(fields) == 0:
      return None

    if "rating" in fields:
      # grab the old review
      old = self.getReview(_id)

      # return if DNE
      if old is None:
        return None

      # attempt to update in the db
      res = self.client.reviews.find_one_and_update(
        { "_id": _id }, { "$set": fields },
        return_document = ReturnDocument.AFTER
      )

      # grab the drink 
      drink = self.getDrink(res["drink_id"])
      drink.sum -= old.rating
      drink.update_rating(res["rating"])

      # update the drink
      self.updateDrink(drink._id, { "rating": drink.rating, "sum": drink.sum })

      return (self.toReview(res), drink.rating)
    else:
      # attempt to update in the db
      res = self.client.reviews.find_one_and_update(
        { "_id": _id }, { "$set": fields },
        return_document = ReturnDocument.AFTER
      )
      return self.toReview(res) if res else None

  def deleteReview(self, review_id: ObjectId) -> bool:
    """Deletes a Review by _id in the db.

      Arguments:
        - review_id { ObjectId }

      Returns:
          - `bool`: True if the review was removed, False otherwise.
    """
    res = self.client.reviews.find_one_and_delete({ '_id': review_id })
    if not res:
      return False
    
    # update the drink
    self.detachReview(res['drink_id'], review_id, res['rating'])
    # update the user
    self.detachItem('review', res['user_email'], review_id)
    return True

  def sampleReviews(self, size: int) -> list[Review]:
    """Returns size random reviews from the database

      Arguments:
        - size { int }: the number of random reviews to be retrieved

      Raises:
        - `ValueError`: Raised if size is not a non-zero positive integer.
      
      Returns:
        - `list[Review]`: A list of random reviews.
    """
    if size < 0:
      raise ValueError("Parameter `size` must be a positive non-zero integer.")

    res = self.client.reviews.aggregate([{ "$sample": { "size": size } }])
    return [ self.toReview(review) for review in res ]
  
  # endregion

  # region Drink

  def getDrink(self, _id: ObjectId) -> Drink or None:
    """Gets a Drink by _id.
      
      Returns:
        - `Drink or None`: Drink object if the Drink exists. `None` otherwise.
    """
    res = self.client.drinks.find_one({ '_id': _id })
    return self.toDrink(res) if res else None

  def createDrink(self, user_email: str, name: str, ingredients: list, img: str) -> Drink:
    """Creates a Drink in the db and returns it.

      Arguments:
        - user_email { str }
        - ingredients { list }
      
      Returns:
        - `Drink`: The newly created Drink. If the drink already exists, returns it.
    """
    existing_drink = self.client.drinks.find_one({ 'user_email': user_email, 'name': name })
    if existing_drink:
      return self.toDrink(existing_drink)

    # create new Drink
    temp = Drink(user_email, name, ingredients, img)
    doc = vars(temp).copy()
    doc['review_ids'] = list(doc['review_ids'])

    # insert drink into db
    temp._id = self.client.drinks.insert_one(doc).inserted_id

    # add drink id to this user
    self.attachItem('drink', user_email, temp._id)
    return temp
  
  def getReviews(self, drink_id: ObjectId) -> list[Review]:
    """Returns a list of Reviews attached to this drink.

      Arguments:
        - drink_id { ObjectId }
    """
    qres = self.client.drinks.find_one({ '_id': drink_id }, { '_id': 0, 'review_ids': 1 })

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
        - `None`: if Drink DNE.
    """    
    # attempt to update in db
    res = self.client.drinks.find_one_and_update(
      { "_id": _id }, { "$set": fields },
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
    # delete the drink from the DB
    res = self.client.drinks.find_one_and_delete({ "_id": _id })
    if not res:
      return False
    
    # delete the drink from the user
    self.detachItem("drink", res["user_email"], _id)

    # remove reviews attached to this drink
    self.client.reviews.delete_many({ "_id": { "$in": res["review_ids"] } })
    return True

  def sampleDrinks(self, size: int) -> list[Drink]:
    """Returns size random drinks from the database

      Arguments:
        - size { int }: the number of random drinks to be retrieved

      Raises:
        - `ValueError`: Raised if size is not a non-zero positive integer.
      
      Returns:
        - `list[Drink]`: A list of random drinks.
    """
    if size < 0:
      raise ValueError("Parameter `size` must be a positive non-zero integer.")

    res = self.client.drinks.aggregate([{ "$sample": { "size": size } }])
    return [ self.toDrink(drink) for drink in res ]

  # endregion

  # region internal functions

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

  def toDrink(self, doc: dict) -> Drink:
    """Converts a MongoDB document to a Drink.

      Arguments:
        - doc { dict }: a document representing a Drink
      
      Returns:
        - `Drink`
    """
    res = Drink(doc['user_email'], doc['name'], doc['ingredients'], doc["img"])
    for k, v in doc.items():
      setattr(res, k, v)
    res.review_ids = set(doc["review_ids"])
    return res

  def attachReview(
    self, drink_id: ObjectId, review_id: ObjectId, rating: int
  ):
    """Attach a review to the drink specified by _id.

      Arguments:
        - drink_id { ObjectId }
        - review_id { ObjectId }
        - drink_hint { Drink, optional }: Providing a Drink for hint will prevent
          getting the Drink from the database. Defaults to None.
        - review_hint { Review, optional }: Providing a Review for hint will prevent
          getting the Review from the database. Defaults to None.

      Raises:
        - `KeyError`: raised if Drink with the given _id DNE.
    """
    # attempt to update db
    drink = self.client.drinks.find_one_and_update(
      { '_id': drink_id },
      { '$addToSet': { 'review_ids': review_id } },
      return_document = ReturnDocument.AFTER
    )

    if not drink:
      raise KeyError(f"Drink with _id {drink_id} DNE")
    
    # update the local drink
    drink = self.toDrink(drink)
    drink.update_rating(rating)
    self.updateDrink(drink_id, { 'rating': drink.rating, "sum": drink.sum })

  def detachReview(self, drink_id: ObjectId, review_id: ObjectId, rating: int):
    """Detaches the review with the associated _id from this drink.

      Arguments:
        - drink_id { ObjectId }
        - review_id: { ObjectId }
        - hint { Drink, optional }: Providing a User for hint will prevent getting the User
          from the database. Defaults to None.

      Raises:
        - `KeyError`: raised if User with the given email (email param or hint.email) DNE.
    """
    # attempt to update db
    drink = self.client.drinks.find_one_and_update(
      { '_id': drink_id },
      { '$pullAll': { "review_ids": [review_id] } }
    )

    if not drink:
      raise KeyError(f"Drink with drink_id {drink_id} DNE")

    # update the local drink
    drink = self.toDrink(drink)
    drink.update_rating(-rating)
    self.updateDrink(drink_id, { 'rating': drink.rating, "sum": drink.sum })

  def attachItem(self, type: str, email: str, _id: ObjectId):
    """Attach an item to the User given the user's email and item's _id.

      Arguments:
        - type { str }: Must be one of ['drink', 'favorite', 'review'].
        - email { str }
        - _id { ObjectId }

      Raises:
         - `KeyError`: raised if User with the given email (email param or hint.email) DNE.
    """
    # grab the user

    # attempt to update db
    res = self.client.users.find_one_and_update(
      { 'email': email },
      { '$addToSet': { f"{type}_ids": _id } }
    )
    # check if update failed
    if not res:
      raise KeyError(f"User with email `{email}` DNE")

  def detachItem(self, type: str, email: str, _id: ObjectId):
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
    # attempt to update db
    res = self.client.users.find_one_and_update(
      { 'email': email },
      { '$pullAll': { f"{type}_ids": [_id] } }
    )
    # check if update failed
    if not res:
      raise KeyError(f"User with email `{email}` DNE")

    # convert to user
    self.toUser(res).remove_item(type, _id)

  def seed(self) -> None:
    # create four users
    andy = self.createUser('andy', 'mina', 'andy@gmail.com', '123')
    jing = self.createUser('jing', 'wen', 'jing@gmail.com', '123')
    steph = self.createUser('steph', 'yung', 'steph@gmail.com', '123')
    sony = self.createUser('sony', 'singh', 'sony@gmail.com', '123')

    # create two drinks
    andy_drink = self.createDrink(
      andy.email,
      "Andy's Drink",
      [ ["strawberry", "4"], ["caramel", "2 pumps"], ["whipped cream", "4 oz"] ]
    )

    jing_drink = self.createDrink(
      jing.email,
      "Jing's Drink",
      [ ["blueberry", "2"], ["lemonade", "16 oz"], ["iced", ""] ]
    )

    # reviews for every drink
    self.createReview(
      jing.email,
      andy_drink._id,
      "As a cold brew fan, I was excited to try it, but I also was concerned it was still going to \
      be too sweet for my taste. Still, I am always up for a fun experiment! It’s not like a total \
      sugar-bomb bright-pink Frappuccino concoction with extra whip.",
      3
    )

    self.createReview(
      steph.email,
      andy_drink._id,
      "I actually LOVED it — and was surprised. At first I just tasted the cold brew, no pumpkin. \
      If your straw is fully in the cup, you don’t taste the pumpkin at all — it’s literally just \
      classic cold brew. Then I just lifted by straw to try the foam alone, and the pumpkin cream \
      was actually so good. REALLY. It was light and creamy, but also rich-tasting, with some good \
      froth and a sweet pumpkin flavor that wasn’t overwhelmingly sweet",
      5
    )

    self.createReview(
      andy.email,
      jing_drink._id,
      "It's pretty similar to that Vanilla Sweet Cream Cold Brew we all know and love, but with a \
      pumpkin cream foam instead",
      4
    )

    self.createReview(
      sony.email,
      jing_drink._id,
      "After a few minutes it kind of all swirls together. You still get that rich, strong cold \
      brew flavor but with a soothing sweet finish",
      2
    )

  # endregion