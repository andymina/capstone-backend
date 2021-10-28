from re import A
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from dotenv import load_dotenv  

app = Flask(__name__) # init flask
CORS(app) # CORS friendly
api = Api(app) # prepare to accept resources

# load env vars
if not load_dotenv():
  app.logger.error('FATAL: Failed to load .env')
  exit()
app.logger.info('.env loaded')

# TODO: ADD RESOURCES HERE

if __name__ == "__main__":
  from os import environ
  app.run(
    debug = True,
    threaded = True,
    host = '0.0.0.0',
    port = environ.get('PORT', 5000)
  )