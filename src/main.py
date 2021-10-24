from flask import Flask
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv  

# init flask
app = Flask(__name__)
cors = CORS(app, origins=['*'])
app.config['CORS_HEADERS'] = 'Content-Type'

# load env vars
if not load_dotenv():
  app.logger.error('FATAL: Failed to load .env')
  exit()
app.logger.info('.env loaded')

from blueprints import UserBP, DrinkBP, ReviewBP

# register blueprints
app.register_blueprint(UserBP.api)
app.register_blueprint(DrinkBP.api)
app.register_blueprint(ReviewBP.api)

# region live test
from db.driver import DBdriver
d = DBdriver(app.logger)
andy = d.getUser('andy@gmail.com')
jing = d.getUser('jing@gmail.com')
drink = d.createDrink(andy.email, "Andy's Drink", [["strawberry", "4"]])
review = d.createReview(jing.email, drink._id, "It's great!", 5)

# endregion

if __name__ == "__main__":
  from os import environ
  app.run(
    debug = True,
    threaded = True,
    host = '0.0.0.0',
    port = environ.get('PORT', 5000)
  )