from flask import Flask
import threading
import time
import requests
from bs4 import BeautifulSoup
from pushbullet import Pushbullet
app = Flask(__name__)
URL = "https://shop.amul.com/en/product/amul-chocolate-whey-protein-34-g-or-pack-of-60-sachets"
CHECK_INTERVAL = 900
PUSHBULLET_API_KEY = "o.d496G7oXop97Fd0k6dq5GSrv4lDJlMoa"
def check_availability():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    status_element = soup.find("div", class_="stock-status")
    return status_element and "Sold Out" not in status_element.text
def send_notification():
    pb = Pushbullet(PUSHBULLET_API_KEY)
    pb.push_note("Product Available!", f"The product is now in stock: {URL}")
def monitor():
    while True:
        if check_availability():
            send_notification()
            break
        time.sleep(CHECK_INTERVAL)
@app.route("/")
def home():
    return "Monitoring service is running!"
if __name__ == "__main__":
    threading.Thread(target=monitor).start()
    app.run(host="0.0.0.0", port=10000)
