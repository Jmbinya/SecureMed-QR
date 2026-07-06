import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY          = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SESSION_TYPE        = "filesystem"
    SESSION_PERMANENT   = False
    SESSION_USE_SIGNER  = True
    PBKDF2_ITERATIONS   = 600_000
    OTP_WINDOW          = 1
    