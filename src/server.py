from dotenv import load_dotenv
from flask import Flask
from blueprints import UserBP, DrinkBP, ReviewBP

# load env vars
msg = '.env loaded' if load_dotenv() else 'Failed to load .env'
print(msg)

# init flask
app = Flask(__name__)

# register blueprints
app.register_blueprint(UserBP.api)
app.register_blueprint(DrinkBP.api)
app.register_blueprint(ReviewBP.api)

if __name__ == "__main__":
  app.run(debug = True)