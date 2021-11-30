import re

# 1 number, 1 lower, 1 upper, 1 special char
pw_regex = r"(?=.*\d+)(?=.*[a-z]+)(?=.*[A-Z]+)(?=.*[!#()-*_&]+)"
email_regex = r"[\w\d-_+\.]+@[[\w\d-_+\.]+\.[\w\d-_]+"
fname_regex = r"[\w-]+"
lname_regex = r"[\w-]+[ \w\d]+\.{0,1}"

def validate_sign_up(form) -> dict[str, str]:
  errors = {}

  # check all fields exists and not empty
  pretty_err = {
    "fname": "First name",
    "lname": "Last name",
    "email": "Email",
    "pw": "Password"
  }

  for field in ["fname", "lname", "email", "pw"]:
    if field not in form:
      errors[field] = f"{pretty_err[field]} is required"
    elif len(form[field]) == 0:
      errors[field] = f"{pretty_err[field]} cannot be empty"

  if len(errors) > 0:
    return errors

  # check fname, lname against regex
  if not re.match(fname_regex, form["fname"]):
    errors["fname"] = "First name can only contain letters and dashes"
  if not re.match(lname_regex, form["lname"]):
    errors["lname"] = "Last name can only contain letters, dashes, numbers, and periods"

  # check email against regex
  if not re.match(email_regex, form["email"]):
    errors["email"] = "Invalid email format"
  
  # check pw against regex
  if not re.match(pw_regex, form["pw"]):
    errors["pw"] = "Password must contain at least one uppercase letter, one lowercase\
    letter, one number, and one special character"
  if not 6 < len(form["pw"]) < 18:
    errors["pw"] = "Password must be betwee 6 and 18 characters"

  return errors