

# 1 number, 1 lower, 1 upper, 1 special char
pass_regex = r"(?=.*\d+)(?=.*[a-z]+)(?=.*[A-Z]+)(?=.*[!#()-*_&]+)"
# wip
email_regex r"(?=.[^\w\d\.])(?:.*\w*)(?:.*\d*)(?:.*\.*)@(?=.*\w+)(.*\.+)(?=.*\w+)"
def validate_sign_up(form) -> dict[str, str]:
  errors = {}
  # check all fields exists
  if "email" not in form:
    errors = { ""}