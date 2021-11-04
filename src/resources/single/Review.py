from db.driver import DBdriver
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort, fields

app = Flask(__name__)
api = Api(app)

reviews = {
    1: {"comment": "review1 ", "summary": "1 "},
    2: {"comment": "review2 ", "summary": "2 "},
    3: {"comment": "review3 ", "summary": "3 "}
}

review_post_args = reqparse.RequestParser()
review_post_args.add_argument("summary", type=str, help="Summary is required.", required = True)

review_put_args = reqparse.RequestParser()
review_put_args.add_argument("summary", type=str)

resource_fields = {
    'id': fields.Integer,
    'summary': fields.String
}
class SingleReview(Resource):
    def get(self):
        return reviews
class Review(Resource):
    def get(self, review_id):
        return reviews[review_id]
    def post(self, review_id):
        args = review_post_args.parse_args()
        if review_id in reviews:
            abort(409, "review id already taken")
        reviews[review_id] = {"review" : args["review"], "summary": args["summary"]}
        return reviews['review_id']
    def put(self, review_id):
        args = review_put_args.parse_args()
        if review_id not in reviews:
            abort(404, message="summary doesn't exist, cannot update.")
        if args['summary']:
            reviews[review_id]['summary'] = args['summary']
        if args['summary']:
            reviews[review_id]['summary'] = args['summary']
        return reviews[review_id]

    def delete(self, review_id):
        del reviews[review_id]
        return reviews

api.add_resource(Review, '/reviews/<string:_id>')
api.add_resource(ReviewList, '/reviews')

if __name__ == '__main__':
    app.run(debug=True)