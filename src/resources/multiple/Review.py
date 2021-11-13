from bson import ObjectId
from db.driver import DBdriver
from flask_restful import Resource, reqparse

class MultipleReview(Resource):

  def __init__(self) -> None:
    self.db = DBdriver()
    self.drink_dne = {
      "data": {
        "res": None,
        "err": "Review with the _id DNE"
      }
    }, 404
    self.parser = reqparse.RequestParser(bundle_errors = True)

  def get(self) -> tuple[dict, int]:
    self.parser.add_argument("_ids", type = str, action = "append")
    self.parser.add_argument("sample", type = int)

    args = self.parser.parse_args()

    if args["_ids"] is not None and args["sample"] is not None:
      return ({"data": { "err": "Cannot pass both _ids and sample parameters; choose one." } }, 400)
    elif args["_ids"] is not None:
      if not len(args["_ids"]):
        return ({ "data": { "err": "Parameter `_ids` cannot be empty." } }, 400)

      res = []
      for _id in args["_ids"]:
        review = self.db.getReview(ObjectId(_id))
        res.append(None if review is None else review.toJSON())
    else:
      sample = 10 if args["sample"] is None else args["sample"]
      res = [ review.toJSON() for review in self.db.sampleReviews(sample) ]

    return ({ "data": res }, 200)

  def post(self) -> tuple[dict, int]:

    self.parser.add_argument('user_email', type = str)
    self.parser.add_argument('drink_id', type = str)
    self.parser.add_argument('comment', type = str)
    self.parser.add_argument('rating', type = int)

    args = self.parser.parse_args()
    email, drink_id, comment, rating = params = (args['user_email'], args["drink_id"], args["comment"], args["rating"])

    if None in params:
      return ({ "data": { "err": "Missing one of ['user_email', 'drink_id', 'comment', 'rating']" } }, 400)
    if not len(comment):
      return ({ "data": { "err": "Parameter `comment` cannot be empty." } }, 400)

    res = self.db.createReview(email, ObjectId(drink_id), comment, rating)
    return ({ "data": res.toJSON() }, 201)

  def delete(self) -> tuple[dict, int]:
    self.parser.add_argument("_ids", type = str, action = "append")
    args = self.parser.parse_args()

    if args["_ids"] is None:
      return ({ "data": { "err": "Parameter `_ids` required." } }, 400)
    elif not len(args["_ids"]):
      return ({ "data": { "err": "parameter `_ids` cannot be empty." } }, 400)

    res = [ _id for _id in args["_ids"] if self.db.deleteReview(ObjectId(_id)) ]
    return ({ "data": res }, 200)