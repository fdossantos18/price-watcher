import csv 
import os 
from datetime import datetime
import requests
import json 

API_URL = "https://api.reverb.com/api/listings"
SEARCH_QUERY = "Yamaha CK61"
TARGET_PRICE = 900
MIN_PLAUSIBLE_PRICE = 300
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
    result = search_listings(SEARCH_QUERY)
    data = result.json()
    print("Total listings found:", data["total"], "| Pages:", data["total_pages"])

    listings = [summarize(l) for l in data["listings"]]
    print("Listings retrieved:", len(listings))

    listings = [l for l in listings if l["price"] >= MIN_PLAUSIBLE_PRICE]
    log_listings(listings)
    deals = [l for l in listings if l["price"] <= TARGET_PRICE]
    deals.sort(key=lambda l: l["price"])

    print(f"{len(deals)} listing(s) at or below ${TARGET_PRICE}:")
    for l in deals:
        print(f"${l['price']:.2f} | {l['condition']} | {l['name']}")
        print(f"   {l['url']}")
    


