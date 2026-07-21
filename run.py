import socket
from app import create_app

# ── Auto-detect LAN IP and inject into config ──
LAN_IP = None
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0.1)
    s.connect(("8.8.8.8", 80))
    LAN_IP = s.getsockname()[0]
    s.close()
except Exception:
    LAN_IP = "127.0.0.1"

app = create_app()

# Override BASE_URL with detected LAN IP if not already set in .env
if not app.config.get("BASE_URL"):
    app.config["BASE_URL"] = f"http://{LAN_IP}:5000"

if __name__ == "__main__":
    print(f"\n🌐 Your LAN IP is: {LAN_IP}")
    print(f"📱 On your phone, visit http://{LAN_IP}:5000")
    print(f"🔗 QR codes will encode: http://{LAN_IP}:5000/scan/<qr_id>\n")

    # 0.0.0.0 makes Flask accessible from other devices on your network
    app.run(debug=True, host="0.0.0.0", port=5000)
