import re

#check if password is valid
def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$#%!])[A-Za-z\d@$#%!]{8,20}$"
    if not re.match(reg, password):
        return False, "Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character from @$#%!."
    
    return True, "Password is valid."