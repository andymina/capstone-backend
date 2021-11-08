from db.driver import DBdriver
from bson import ObjectId
from flask_restful import Resource, reqparse
class SingleReview(Resource):
    """API for single review endpoints.

       All routes return a JSON object and an HTTP status code.

       Returns for each route are broken into two categories: potential JSON and status codes.
       All returns have a `data` key where the value is either specified or an object containing
       the specified data.

       If there is errors in execution, retusns a JSON object with the following structure:

       ```{
           "data": {
               "res": as sepfified,
               "err": error message
           }
       }
    """
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
        """ Gets the Review with the associated ObjectId.
        Route
        <String> _id: ObjectId of the review to be retrieved.
        Returns: null if a review with the given ObjectId DNE. Otherwise, Review.

        """

        res = self.db.getReview(ObjectId(_id))
        return self.review_dne if not res else { "data": res.toJSON() }, 200

    def put(self, _id: str) -> tuple[dict, int]:
        """Given an object where the (key, value) pairs are the fields to be updated,
        updates the review in the database and returns the updated review.
        Parameters:
        Route
        <String> _id: ObjectId of the review to be updated.
        API
        <Object> fields: key represents the property name to updated. value represents the new value.
        Returns: updated Review. If review's rating was updated returns an Object of the following structure:
        """

        args = self.parser.parse_args()

        if args["fields"] is None:
            return { "data": { "err": "Missing fields parameter." }}, 400
        elif not len(args["fields"]):
            return { "data": { "err": "Parameter 'fields' cannot be empty." }}, 400

        res = self.db.updateReview(ObjectId(_id), args["fields"])
        return self.review_dne if not res else { "data": res.toJSON(), }, 200

    def delete(self, _id: str) -> tuple[dict, int]:
        """Deletes the review with the given _id.
        Route
        <String> _id: ObjectId of the review to be deleted.
        Returns: null if no review was deleted. If a review was deleted,
        returns Object of the following structure:
        """

        res = self.db.deleteReview(ObjectId(_id))
        return self.review_dne if not res else { "data": res.toJSON(), }, 200
