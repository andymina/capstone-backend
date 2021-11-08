from db.driver import DBdriver
from bson import ObjectId
from flask_restful import Resource, reqparse
class SingleReview(Resource):
    def __init__(self) -> None:
        self.db = DBdriver()
        self.review_dne = {
            "data": {
                "res": None,
                "err": "Review with that _id DNE"
            }
        }, 404
        self.parser = reqparse.RequestParser(bundle_errors = True)
        self.parser.add_argument('fields', type = dict)

    def get(self, _id: str) -> tuple[dict, int]:
        res = self.db.getReview(ObjectId(_id))
        return self.review_dne if not res else { "data": res.toJSON() }, 200

    def put(self, _id: str) -> tuple[dict, int]:
        args = self.parser.parse_args()

        if args["fields"] is None:
            return { "data": { "err": "Missing fields parameter." }}, 400
        elif not len(args["fields"]):
            return { "data": { "err": "Parameter 'fields' cannot be empty." }}, 400

        res = self.db.updateReview(ObjectId(_id), args["fields"])
        return self.review_dne if not res else { "data": res.toJSON(), }, 200

    def delete(self, _id: str) -> tuple[dict, int]:
        res = self.db.deleteReview(ObjectId(_id))
        return self.review_dne if not res else { "data": res.toJSON(), }, 200
