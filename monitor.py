import os
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
URL = "https://shop.amul.com/en/product/amul-chocolate-whey-protein-34-g-or-pack-of-60-sachets"
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))  # seconds
PUSHBULLET_API_KEY = os.getenv("PUSHBULLET_API_KEY")
app = Flask(__name__)
def check_availability():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    # TODO: refine this selector by inspecting the page HTML
    status_element = soup.find("div", class_="stock-status")
    return bool(status_element and "Sold Out" not in status_element.get_text(strip=True))
def send_pushbullet(title: str, body: str):
    if not PUSHBULLET_API_KEY:
        print("PUSHBULLET_API_KEY is not set; cannot send notification.")
        return
    headers = {
        "Access-Token": PUSHBULLET_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"type": "note", "title": title, "body": body}
    resp = requests.post("https://api.pushbullet.com/v2/pushes",
                         headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    print("Pushbullet notification sent.")
def monitor_loop():
    print("Monitor loop started.")
    while True:
        try:
            if check_availability():
                send_pushbullet("Product Available!",
                                f"The product is now in stock: {URL}")
                # Optional: break after first success
                break
            else:
                print("Still sold out. Rechecking in", CHECK_INTERVAL, "seconds.")
        except Exception as e:
            # Keep going even if a single check fails
            print("Error while checking:", repr(e))
        time.sleep(CHECK_INTERVAL)
@app.route("/")
def health():
    return "Amul monitor is running ✅"
# Start background thread when the web service starts.
threading.Thread(target=monitor_loop, daemon=True).start()

