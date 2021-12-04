from db.driver import DBdriver
import bcrypt

# class AuthHandler:
#   def __init__(self):
#     self.db = DBdriver()
db = DBdriver()
def authenticate(email: str, pw: str):
  # make sure the user exists
  user = db.getUser(email)
  if user is None:
    return user

  # check pws
  pw_match = bcrypt.checkpw(user.pw.encode("utf-8"), pw.encode("utf-8"))
  if pw_match:
    return user

def identify(jwt_payload: dict[str, str]):
  return jwt_payload