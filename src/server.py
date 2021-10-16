from flask import Flask
from dotenv import load_dotenv

# init flask
app = Flask(__name__)

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

if __name__ == "__main__":
  app.run(debug = True)