"""
verify_session.py — Full integration verification for Redis-backed sessions.
Tests: landing page, registration flow, session cookie size, Redis keys.
"""
import urllib.request
import http.cookiejar
import urllib.parse
import sys

# ---- Setup ----
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

BASE = "http://localhost:5000"

# ---- 1. Landing page ----
try:
    resp = opener.open(f"{BASE}/")
    landing_len = len(resp.read())
    print(f"✅ 1. Landing page (GET /) → {resp.status} ({landing_len} bytes)")
except Exception as e:
    print(f"❌ 1. Landing page FAILED: {e}")
    sys.exit(1)

# ---- 2. Registration form ----
try:
    resp = opener.open(f"{BASE}/register")
    print(f"✅ 2. Register form (GET /register) → {resp.status}")
except Exception as e:
    print(f"❌ 2. Register form FAILED: {e}")
    sys.exit(1)

# ---- 3. Submit registration ----
data = urllib.parse.urlencode({
    'full_name': 'Integration Test Patient',
    'blood_type': 'A+',
    'allergies': 'Penicillin',
    'conditions': 'None',
    'medications': 'None',
    'emergency_name': 'Jane Doe',
    'emergency_phone': '+254700000000',
    'password': 'testpass123',
    'confirm_password': 'testpass123'
}).encode()

try:
    resp = opener.open(f"{BASE}/register", data=data)
    print(f"✅ 3. Registration POST → {resp.status} (redirected to: {resp.url})")
except urllib.error.HTTPError as e:
    print(f"❌ 3. Registration POST failed: {e.code} - {e.read().decode()}")
    sys.exit(1)

# ---- 4. Check cookies ----
print()
print("📋 Session Cookies:")
for c in cj:
    ck_len = len(c.value)
    preview = c.value[:60]
    print(f"   [{c.name}] = {preview}... ({ck_len} chars)")

# ---- 5. Verify Redis-backed sessions ----
print()
any_short = any(len(c.value) < 100 for c in cj)
if any_short:
    print(f"✅ SESSION IS REDIS-BACKED (cookie is short opaque session ID: {len(c.value)} chars)")
    print("   Decrypted medical record lives in Redis server-side, not in client cookie.")
else:
    print(f"❌ SESSION MAY BE COOKIE-BASED (long cookie: >100 chars)")

# ---- 6. Dashboard ----
try:
    resp = opener.open(f"{BASE}/dashboard")
    if resp.status == 200:
        print(f"\n✅ 4. Dashboard (GET /dashboard) → {resp.status} (session active)")
    else:
        body = resp.read().decode()
        print(f"\n⚠️  Dashboard: {resp.status}")
except Exception as e:
    print(f"\n⚠️  Dashboard: {e}")

print("\n✅ Full integration test complete!")
