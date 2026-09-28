import requests
import json 

API_URL = "https://api.reverb.com/api/listings"
SEARCH_QUERY = "Yamaha CK61"
TARGET_PRICE = 900
MIN_PLAUSIBLE_PRICE = 300


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
        "name": listing.get("name") or listing.get("model"),
        "condition": listing["condition"]["display_name"],
        "price": listing["price"]["amount_cents"] / 100,
        "url": listing.get("_links", {}).get("web", {}).get("href"),
    }

if __name__ == "__main__":
    result = search_listings(SEARCH_QUERY)
    data = result.json()
    print("Total listings found:", data["total"], "| Pages:", data["total_pages"])

    listings = [summarize(l) for l in data["listings"]]
    print("Listings retrieved:", len(listings))

    listings = [l for l in listings if l["price"] >= MIN_PLAUSIBLE_PRICE]
    deals = [l for l in listings if l["price"] <= TARGET_PRICE]
    deals.sort(key=lambda l: l["price"])

    print(f"{len(deals)} listing(s) at or below ${TARGET_PRICE}:")
    for l in deals:
        print(f"${l['price']:.2f} | {l['condition']} | {l['name']}")
        print(f"   {l['url']}")
    


