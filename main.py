import csv 
import os 
from datetime import datetime
import requests
import json 

API_URL = "https://api.reverb.com/api/listings"
SEARCH_QUERY = "Yamaha CK61"
TARGET_PRICE = 900
MIN_PLAUSIBLE_PRICE = 300
MIN_DROP_TO_ALERT = 5.00
CSV_FILE = "prices.csv"


def search_listings(query):
    headers = {
        "Accept": "application/hal+json",
        "Accept-Version": "3.0",
    }
    params = {"query": query, "per_page": 50}
    response = requests.get(API_URL, headers=headers, params=params)
    return response


def summarize(listing):
    return {
        "id": listing["id"],
        "name": listing.get("name") or listing.get("model"),
        "condition": listing["condition"]["display_name"],
        "price": listing["price"]["amount_cents"] / 100,
        "url": listing.get("_links", {}).get("web", {}).get("href"),
    }


def load_last_known_prices():
    last_seen = {}
    if not os.path.exists(CSV_FILE):
        return last_seen

    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            listing_id = int(row["id"])
            price = float(row["price"])
            last_seen[listing_id] = price 
    return last_seen



def log_listings(listings):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["checked_at", "id", "name", "condition", "price", "url"])
        now = datetime.now().isoformat(timespec="seconds")
        for l in listings:
            writer.writerow([now, l["id"], l["name"], l["condition"], l["price"], l["url"]])



if __name__ == "__main__":
    last_known = load_last_known_prices()

    result = search_listings(SEARCH_QUERY)
    data = result.json()
    print("Total listings found:", data["total"], "| Pages:", data["total_pages"])

    listings = [summarize(l) for l in data["listings"]]
    listings = [l for l in listings if l["price"] >= MIN_PLAUSIBLE_PRICE]
    print("Listings retrieved:", len(listings))

    log_listings(listings)

    alerts = []
    for l in listings:
        if l["price"] > TARGET_PRICE:
            continue # not a deal, skip it 

        previous_price = last_known.get(l["id"])
        if previous_price is None:
            alerts.append((l, "NEW"))
        elif previous_price - l["price"] >= MIN_DROP_TO_ALERT:
            alerts.append((l, f"DROPPED from ${previous_price:.2f}"))

    if not alerts:
        print("No new or dropped deals since last check.")
    else:
        print(f"\n{len(alerts)} alerts(s):")
        for l, reason in alerts:
            print(f"[{reason}] ${l['price']:.2f} | {l['condition']} | {l['name']}")
            print(f"   {l['url']}")


    


