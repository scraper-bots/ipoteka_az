import asyncio
import aiohttp
import csv
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://ipoteka.az"
FRAGMENT_URL = "https://ipoteka.az/search/fragment"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "text/html, */*; q=0.01",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://ipoteka.az/search",
}

# Concurrency settings
MAX_CONCURRENT_REQUESTS = 10
DELAY_BETWEEN_REQUESTS = 0.3


def get_search_params(page=1):
    """Get search parameters for the fragment endpoint."""
    return {
        "ad_type": "0",
        "adsTextSearch": "",
        "min_area": "",
        "max_area": "",
        "min_price": "",
        "max_price": "",
        "city_id": "-",
        "initial_payment": "",
        "monthly_payment": "",
        "document_type": "-",
        "search_type": "0",
        "page": str(page),
    }


def get_text_by_label(soup, label):
    """Extract text value by label from property page."""
    # Try stats section
    stats_div = soup.find("div", class_="stats")
    if stats_div:
        label_div = stats_div.find("div", string=lambda t: t and label in t if t else False)
        if label_div:
            next_div = label_div.find_next_sibling("div")
            if next_div:
                return next_div.get_text(strip=True)

    # Try params_block section
    params_block = soup.find("div", class_="params_block")
    if params_block:
        for rw in params_block.find_all("div", class_="rw"):
            divs = rw.find_all("div")
            for i, div in enumerate(divs):
                if div.get_text(strip=True) == label and i + 1 < len(divs):
                    return divs[i + 1].get_text(strip=True)

    return None


def extract_property_info(soup):
    """Extract floor, area, rooms, document from property-info block."""
    result = {"floor": None, "area": None, "room_count": None, "document_type": None}

    prop_info = soup.find("div", class_="property-info")
    if not prop_info:
        return result

    divs = prop_info.find_all("div")
    labels = []
    values = []

    for div in divs:
        if "label" in div.get("class", []):
            labels.append(div.get_text(strip=True))
        else:
            values.append(div.get_text(strip=True))

    # Map labels to values
    label_map = {
        "Mərtəbə": "floor",
        "Sahə": "area",
        "Otaq": "room_count",
        "Sənəd": "document_type",
    }

    for i, label in enumerate(labels):
        if label in label_map and i < len(values):
            result[label_map[label]] = values[i]

    return result


async def fetch(session, url, params=None):
    """Fetch a URL with error handling."""
    try:
        async with session.get(url, params=params, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=30)) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


async def get_property_links(session, page):
    """Fetch property links from a search results page."""
    params = get_search_params(page)
    html = await fetch(session, FRAGMENT_URL, params)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/elan/" in href:
            full_url = urljoin(BASE_URL, href)
            if full_url not in links:
                links.append(full_url)

    return links


async def scrape_property(session, url, semaphore):
    """Scrape details from a single property page."""
    async with semaphore:
        await asyncio.sleep(random.uniform(0.1, DELAY_BETWEEN_REQUESTS))

        html = await fetch(session, url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # Extract user name - clean up whitespace
        user_div = soup.find("div", class_="user")
        user_name = " ".join(user_div.get_text().split()) if user_div else None

        # Extract phone number
        phone_div = soup.find("div", class_="showNumber")
        phone_number = phone_div.get_text(strip=True) if phone_div else None

        # Extract title from page title or meta
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None

        # Extract price from span.price
        price_span = soup.find("span", class_="price")
        price = price_span.get_text(strip=True) if price_span else None

        # Extract address from desc_block - typically contains location info
        desc_block = soup.find("div", class_="desc_block")
        address = None
        if desc_block:
            # Look for location spans or text
            location_parts = []
            for el in desc_block.find_all(["span", "a"]):
                text = el.get_text(strip=True)
                if text and "m²" not in text and "AZN" not in text and "Otaq" not in text:
                    location_parts.append(text)
            if location_parts:
                address = ", ".join(location_parts[:3])

        # Extract description from text div
        text_div = soup.find("div", class_="text")
        description = text_div.get_text(strip=True) if text_div else None

        # Extract stats
        announcement_id = get_text_by_label(soup, "Elan İD")
        update_date = get_text_by_label(soup, "Yeniləndi")
        view_count = get_text_by_label(soup, "Baxış sayı")

        # Extract property info (floor, area, rooms, document)
        prop_info = extract_property_info(soup)

        # Fallback to params_block for repair type
        repair_type = get_text_by_label(soup, "Təmir") or get_text_by_label(soup, "Təmirin növü")
        building_type = get_text_by_label(soup, "Binanın tipi")

        return {
            "url": url,
            "title": title,
            "price": price,
            "address": address,
            "user_name": user_name,
            "phone_number": phone_number,
            "announcement_id": announcement_id,
            "update_date": update_date,
            "view_count": view_count,
            "area": prop_info["area"],
            "floor": prop_info["floor"],
            "room_count": prop_info["room_count"],
            "document_type": prop_info["document_type"],
            "repair_type": repair_type,
            "building_type": building_type,
            "description": description,
        }


def save_to_csv(data, filename="ipoteka_properties.csv"):
    """Save scraped data to CSV file."""
    if not data:
        print("No data to save.")
        return

    fieldnames = [
        "url", "title", "price", "address", "user_name", "phone_number",
        "announcement_id", "update_date", "view_count", "area", "floor",
        "room_count", "document_type", "repair_type", "building_type", "description"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Saved {len(data)} properties to {filename}")


async def scrape_page_properties(session, page, semaphore):
    """Scrape all properties from a single page."""
    links = await get_property_links(session, page)

    if not links:
        return []

    print(f"Page {page}: Found {len(links)} properties")

    tasks = [scrape_property(session, link, semaphore) for link in links]
    results = await asyncio.gather(*tasks)

    return [r for r in results if r is not None]


async def main():
    all_properties = []
    max_pages = 1000
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    print("Starting async scrape of ipoteka.az...")

    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS, ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        page = 1

        while page <= max_pages:
            print(f"\nProcessing page {page}...")

            properties = await scrape_page_properties(session, page, semaphore)

            if not properties:
                print(f"No properties found on page {page}. Stopping.")
                break

            all_properties.extend(properties)
            print(f"Total scraped so far: {len(all_properties)}")

            # Save progress after each page
            save_to_csv(all_properties)

            page += 1
            await asyncio.sleep(random.uniform(0.5, 1.0))

    print(f"\nScraping complete! Total properties: {len(all_properties)}")
    save_to_csv(all_properties)


if __name__ == "__main__":
    asyncio.run(main())
