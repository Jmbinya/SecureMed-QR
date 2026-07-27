import os
from dotenv import load_dotenv
import redis
load_dotenv()


class Config:
    SECRET_KEY              = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SESSION_TYPE            = "redis"
    SESSION_PERMANENT       = False
    SESSION_USE_SIGNER      = True
    SESSION_KEY_PREFIX      = "securemed:"
    SESSION_REDIS           = redis.from_url((os.environ.get("REDIS_URL") or "redis://localhost:6379").strip())
    RATELIMIT_STORAGE_URI   = os.environ.get("REDIS_URL", "redis://localhost:6379")
    RATELIMIT_STRATEGY      = "fixed-window"

    # ── Cookie security ──────────────────────────────────────────────
    # Secure cookies only in production (when RENDER env var is set).
    # Render automatically sets RENDER=true in its environment.
    SESSION_COOKIE_SECURE   = os.environ.get("RENDER") is not None
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    PBKDF2_ITERATIONS       = 600_000
    OTP_WINDOW              = 1

    # ── LAN / mobile access ──────────────────────────────────────────────
    # Set BASE_URL to your computer's LAN IP so QR codes encode a URL
    # devices on your Wi-Fi can reach.
    # Example: BASE_URL=http://192.168.1.100:5000
    # Leave empty to fall back to request.host_url (localhost).
    BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
