import requests
from bs4 import BeautifulSoup
import time
from pushbullet import Pushbullet

URL = "https://shop.amul.com/en/product/amul-chocolate-whey-protein-34-g-or-pack-of-60-sachets"
CHECK_INTERVAL = 300  # 5 minutes
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

if __name__ == "__main__":
    while True:
        if check_availability():
            send_notification()
            print("Product available! Notification sent.")
            break
        else:
            print("Still sold out. Checking again in 5 minutes...")
        time.sleep(CHECK_INTERVAL)
