import re

email_regex = r"[\w\d+\.]+@[[\w\d+\.]+\.[\w\d]+"
fname_regex = r"[\w-]+"
lname_regex = r"[\w-]+[ \w\d]+\.{0,1}"
upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower = upper.lower()
nums = "1234567890"

def validate(form: dict, mode="login") -> dict[str, str]:
  """Form validator.

    Arguments:
      - form { dict }: k,v pairs of field names and values to checked
      - mode { str, optional }: The type of form to validate. Must be one of ["signup", "login"].
        Defaults to "login"
    
    Returns:
      - `dict[str, str]`: Returns k,v pairs of incorrect fields and the associated errmsgs.
  """
  errors = {}

  # check all fields exists and not empty
  pretty_err = {
    "fname": "First name",
    "lname": "Last name",
    "email": "Email",
    "pw": "Password"
  }
  fields = ["email", "pw"]
  if mode == "signup":
    fields += ["fname", "lname"]

  for field in fields:
    if field not in form:
      errors[field] = f"{pretty_err[field]} is required"
    elif len(form[field]) == 0:
      errors[field] = f"{pretty_err[field]} cannot be empty"

  if len(errors) > 0:
    return errors

  if mode == "signup":
    # check fname, lname against regex
    if not re.match(fname_regex, form["fname"]):
      errors["fname"] = "First name can only contain letters and dashes"
    if not re.match(lname_regex, form["lname"]):
      errors["lname"] = "Last name can only contain letters, dashes, numbers, and periods"

  # check email against regex
  if not re.match(email_regex, form["email"]):
    errors["email"] = "Invalid email format"

  has_upper = False
  while not has_upper:
    for c in upper:
      if c in form["pw"]:
        has_upper = True
        break

  has_lower = False
  while not has_lower:
    for c in lower:
      if c in form["pw"]:
        has_lower = True
        break

  if not has_upper or not has_lower:
    errors["pw"] = "Password must contain at least one uppercase letter and one lowercase letter"
    
  if not 6 <= len(form["pw"]) <= 18:
    errors["pw"] = "Password must be between 6 and 18 characters"

  return errors