import os
from dotenv import load_dotenv

load_dotenv()

class config:
    SECRET_KEY = os.environ.get("SECRET_KEY","change-this-in-production")
    DATABASE = os.path.join("instance","securemed.db")
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    SESSION_USER_SIGNER = True
    PBKDF2_ITERATIONS = 600_000
    OTP_WINDOW = 1