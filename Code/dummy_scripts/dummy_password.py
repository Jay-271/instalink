from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

users = {
    "users": {
        "Alice": "$argon2id$v=19$m=65536,t=3,p=4$TcoxSlVAW8PyPBLoti73hw$TIQQkvNx5rirkDYBWJo6mvM/56O1pTG3qa5vhIVqY4Q",
        "Bob": "$argon2id$v=19$m=65536,t=3,p=4$jIpQuhiCKQrn0SNnKFWEFw$jEVtuYihvyPIGENFpXHc0o4L6lm4MhdsW9mLZyT8WAA",
        "Zebra": "$argon2id$v=19$m=65536,t=3,p=4$wFAxokQCv3vtwPHHQESvcQ$1JpDrposd6YQ3ecNUFeKEXXZDbLbETdYxPSvcfw+1rU"
    }
}
ph = PasswordHasher()
"""
hashed_users = {"users": {}}

for username, password in users["users"].items():
    hashed_users["users"][username] = ph.hash(password)
print(hashed_users)
"""
def validate_password(username, input_password):
    try:
        # Retrieve the stored hash for the username
        stored_hash = users["users"].get(username)
        if not stored_hash:
            print("Username not found!")
            return False
        
        # Verify the input password against the stored hash
        if ph.verify(stored_hash, input_password):
            print(f"Login successful for {username}!")
            return True
    except VerifyMismatchError:
        print("Incorrect password.")
    return False
validate_password("Alice", "password123")  # Should print "Login successful for Alice!"
validate_password("Bob", "wrongPass")      # Should print "Incorrect password."
validate_password("Zebra", "zebra123")     # Should print "Login successful for Zebra!"

"""
{
    "users": {
        "Alice": "$argon2id$v=19$m=65536,t=3,p=4$TcoxSlVAW8PyPBLoti73hw$TIQQkvNx5rirkDYBWJo6mvM/56O1pTG3qa5vhIVqY4Q",
        "Bob": "$argon2id$v=19$m=65536,t=3,p=4$jIpQuhiCKQrn0SNnKFWEFw$jEVtuYihvyPIGENFpXHc0o4L6lm4MhdsW9mLZyT8WAA",
        "Zebra": "$argon2id$v=19$m=65536,t=3,p=4$wFAxokQCv3vtwPHHQESvcQ$1JpDrposd6YQ3ecNUFeKEXXZDbLbETdYxPSvcfw+1rU"
    }
}
"""