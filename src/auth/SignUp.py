from flask_restful import Resource, reqparse
from db.driver import DBdriver
from auth_helper import validate_signup

class SignUp(Resource):
  def __init__(self) -> None:
    self.db = DBdriver()
    self.parser = reqparse.RequestParser()

  def post(self):
    # grab args
    self.parser.add_argument()
    # make sure the form is
    errors = validate_signup()
    pass