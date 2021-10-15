from flask import Flask
from blueprints import UserBP, DrinkBP, ReviewBP

# init flask
app = Flask(__name__)

# register blueprints
app.register_blueprint(UserBP.api)
app.register_blueprint(DrinkBP.api)
app.register_blueprint(ReviewBP.api)
app.run(debug = True)