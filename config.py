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

    # ── LAN / mobile access ──────────────────────────────────────────────
    # Set BASE_URL to your computer's LAN IP so QR codes encode a URL
    # devices on your Wi-Fi can reach.
    # Example: BASE_URL=http://192.168.1.100:5000
    # Leave empty to fall back to request.host_url (localhost).
    BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
    