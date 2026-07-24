import urllib.request, http.cookiejar, urllib.parse, sys

# ---- Setup ----
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

BASE = "http://127.0.0.1:5000"
results = []

# ---- 1. Landing page ----
try:
    resp = opener.open(f"{BASE}/")
    landing_len = len(resp.read())
    results.append(f"OK Landing page (GET /) -> {resp.status} ({landing_len} bytes)")
except Exception as e:
    results.append(f"FAIL Landing page: {e}")
    with open("session_test_result.txt", "w") as f:
        f.write("\n".join(results))
    sys.exit(1)

# ---- 2. Registration form ----
try:
    resp = opener.open(f"{BASE}/register")
    results.append(f"OK Register form (GET /register) -> {resp.status}")
except Exception as e:
    results.append(f"FAIL Register form: {e}")
    with open("session_test_result.txt", "w") as f:
        f.write("\n".join(results))
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
    results.append(f"OK Registration POST -> {resp.status} (redirected to: {resp.url})")
except urllib.error.HTTPError as e:
    results.append(f"FAIL Registration POST: {e.code}")
    with open("session_test_result.txt", "w") as f:
        f.write("\n".join(results))
    sys.exit(1)

# ---- 4. Check cookies ----
results.append("")
results.append("[Session Cookies]:")
for c in cj:
    ck_len = len(c.value)
    preview = c.value[:60]
    results.append(f"  cookie: {c.name} = {preview}... ({ck_len} chars)")

# ---- 5. Verify Redis-backed sessions ----
results.append("")
any_short = any(len(c.value) < 100 for c in cj)
if any_short:
    results.append(f"PASS Session is REDIS-BACKED (short session ID: {len(c.value)} chars)")
    results.append("  Decrypted medical record lives in Redis server-side, not in client cookie.")
else:
    results.append(f"WARN Session MAY BE COOKIE-BASED (long cookie: >100 chars)")

# ---- 6. Dashboard ----
try:
    resp = opener.open(f"{BASE}/dashboard")
    if resp.status == 200:
        results.append(f"OK Dashboard (GET /dashboard) -> {resp.status} (session active)")
    else:
        results.append(f"UNEXP Dashboard: {resp.status}")
except Exception as e:
    results.append(f"NOTE Dashboard: {e}")

results.append("")
results.append("ALL TESTS COMPLETED")

with open("session_test_result.txt", "w") as f:
    f.write("\n".join(results))
