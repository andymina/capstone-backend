from db.driver import DBdriver
import bcrypt

def authenticate(email: str, pw: str):
  # connect to the database 
  db = DBdriver()

  # make sure the user exists
  user = db.getUser(email)
  if user is None:
    return user
  
  # check pws
  pw_match = bcrypt.checkpw(user.pw.encode("utf-8"), pw.encode("utf-8"))
  if pw_match:
    return user

def identify(jwt_payload: dict[str, str]):
  print(jwt_payload)
  # connect to the database 
  db = DBdriver()
  return db.getUser(jwt_payload["email"])

# @jwt.payload_handler
# def make_payload(identity):
#   print(identity)