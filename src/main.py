from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from dotenv import load_dotenv  
from resources import SingleUser, SingleDrink, SingleReview
from resources import MultipleUser, MultipleDrink, MultipleReview

app = Flask(__name__) # init flask
CORS(app) # CORS friendly
api = Api(app) # prepare to accept resources

# load env vars
if not load_dotenv():
  app.logger.error('FATAL: Failed to load .env')
  exit()
app.logger.info('.env loaded')

# SINGLE RESOURCES
api.add_resource(SingleUser, "/users/<string:email>", endpoint = "user")
api.add_resource(SingleDrink, "/drinks/<string:_id>", endpoint = "drink")
api.add_resource(SingleReview, "/reviews/<string:_id>", endpoint = "review")

# MULTIPLE RESOURCES
api.add_resource(MultipleUser, "/users", endpoint = "users")
api.add_resource(MultipleDrink, "/drinks", endpoint = "drinks")
api.add_resource(MultipleReview, "/reviews", endpoint = "reviews")

if __name__ == "__main__":
  from os import environ
  app.run(
    debug = True,
    threaded = True,
    host = '0.0.0.0',
    port = environ.get('PORT', 5000)
  )