# Import necessary libraries
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import aiohttp
from bs4 import BeautifulSoup
import re
from forex_python.converter import CurrencyRates
from decimal import Decimal
import asyncio
import urllib
import sqlite3
import datetime


# Function to create a database connection
def create_connection():
    conn = sqlite3.connect("database.db")
    return conn


# Coroutine to create a table for search results
async def create_table(conn):
    cursor = conn.cursor()
    with conn:
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS searches (
                        id INTEGER PRIMARY KEY,
                        query TEXT NOT NULL,
                        time TEXT NOT NULL,
                        item_name TEXT NOT NULL,
                        amazon_com_price REAL,
                        amazon_co_uk_price REAL,
                        amazon_de_price REAL,
                        amazon_ca_price REAL
                    )
                """)


# Initialize FastAPI app
app = FastAPI()

# Mount the static files directory and set up Jinja2 templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
urls = {}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
}

# Coroutine to execute on app startup - creates the database table
@app.on_event("startup")
async def on_startup():
    db_conn = create_connection()
    await create_table(db_conn)


# Route for the root URL, renders the index.html template
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Function to get the recent search count
def recent_search_count(conn):
    cursor = conn.cursor()
    now = datetime.datetime.now()
    day_ago = now - datetime.timedelta(days=1)
    cursor.execute("SELECT COUNT(*) FROM searches WHERE time > ?", (day_ago.strftime("%Y-%m-%d %H:%M:%S"),))
    count = cursor.fetchone()[0]
    count = count//10 + 1
    return count


# Route for search functionality
@app.get("/search")
async def search(query: str, response: Response):
    conn = create_connection()
    search_count = recent_search_count(conn)
    print(search_count)
    if search_count > 10:
        return {"error": "Daily searches cap reached. Consider upgrading to the premium service in order to search for more items."}
    url = f"https://www.amazon.com/s?k={query}"
    response.headers["Access-Control-Allow-Origin"] = "*"
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    soup = BeautifulSoup(response.read(), "html.parser")

    # Extract relevant data from the search results
    data = [{"name": result.find('h2') and result.h2.text,
             "image_url": result.find('img') and result.img['src'],
             "asin": re.search(r"/dp/(\w{10})", result.find("a", {"class": "a-link-normal"}).get("href")).group(1) if re.search(r"/dp/(\w{10})", result.find("a", {"class": "a-link-normal"}).get("href")) else None}

            for result in soup.select('[data-component-type="s-search-result"]')[:10]]
    # Insert search results

    conn = create_connection()
    cursor = conn.cursor()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for result in data:
        cursor.execute('''INSERT INTO searches (query, time, item_name, amazon_com_price,
                           amazon_co_uk_price, amazon_de_price, amazon_ca_price)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (query, current_time, result['name'], None, None, None, None))
        conn.commit()

    return data

# Route for getting prices from different Amazon sites
@app.get("/get_prices")
async def get_prices(asin: str, query: str, item_name: str):

    sites = {
        "Amazon.com": "https://www.amazon.com",
        "Amazon.co.uk": "https://www.amazon.co.uk",
        "Amazon.de": "https://www.amazon.de",
        "Amazon.ca": "https://www.amazon.ca"
    }
    currency_converter = CurrencyRates()
    prices = {}
    rating = None
    gbp = 1 / (float(currency_converter.get_rate('USD', 'GBP')))
    ca = 1 / (float(currency_converter.get_rate('USD', 'CAD')))
    eur = 1 / (float(currency_converter.get_rate('EUR', 'USD')))

    # Coroutine to fetch the product details from each Amazon site
    async def fetch(site_name, site_url, session, item_name):
        nonlocal rating
        url = f"{site_url}/dp/{asin}"
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), "html.parser")

                if not rating:
                    rating_element = soup.find("span", {"class": "a-icon-alt"})
                    print(rating_element)
                    if rating_element:
                        rating = rating_element.text.split()[0]
                else:None


                price_container = soup.find("span", {"class": "a-price"})
                if price_container:
                    offscreen_price_element = price_container.find("span", {"class": "a-offscreen"})
                    price = offscreen_price_element.text.strip() if offscreen_price_element else None
                else:
                    price = None
                # Fetch and convert prices
                if price_container:
                    price = price_container.find("span", {"class": "a-offscreen"})
                    if price:
                        price = price.text.strip()
                        price_value = Decimal(re.sub(r"[^\d.,]", "", price).replace(",", "."))
                        if site_name == "Amazon.de":
                            price_value = float(price_value)
                            price_usd = eur * price_value
                            price = f"${price_usd:.2f}"
                        elif site_name == "Amazon.co.uk":
                            price_value = float(price_value)
                            price_usd = gbp * price_value
                            price = f"${price_usd:.2f}"
                        elif site_name == "Amazon.ca":
                            price_value = float(price_value)
                            price_usd = ca * price_value
                            price = f"${price_usd:.2f}"
                    else:
                        price = "Not found"
                else:
                    price = "Not found"

                prices[site_name] = price
            else:
                prices[site_name] = "Not found"

    # Fetch prices concurrently using aiohttp
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(site_name, site_url, session, item_name) for site_name, site_url in sites.items()]

        await asyncio.gather(*tasks)

    # Insert fetched prices into the database
    conn = create_connection()
    cursor = conn.cursor()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''INSERT INTO searches (query, time, item_name, amazon_com_price,
                         amazon_co_uk_price, amazon_de_price, amazon_ca_price)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (query, current_time, item_name,
                    float(prices['Amazon.com'].replace('$', '')) if prices['Amazon.com'] != 'Not found' else None,
                    float(prices['Amazon.co.uk'].replace('$', '')) if prices['Amazon.co.uk'] != 'Not found' else None,
                    float(prices['Amazon.de'].replace('$', '')) if prices['Amazon.de'] != 'Not found' else None,
                    float(prices['Amazon.ca'].replace('$', '')) if prices['Amazon.ca'] != 'Not found' else None))
    conn.commit()
    conn.close()

    return {"Item": item_name, "Rating": rating, "Prices": prices,
            "URLs": {site_name: f"{site_url}/dp/{asin}" for site_name, site_url in sites.items()}}

# Route for fetching past searches
@app.get("/past_searches")
async def past_searches():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM searches ORDER BY time DESC')
    data = cursor.fetchall()
    conn.close()

    past_searches = []
    for row in data:
        if row[4] is None and row[5] is None and row[6] is None and row[7] is None:
            continue
        else:
            search = {
                'Query': row[1],
                'Time': row[2],
                'Item name': row[3],
                'Amazon.com price': row[4],
                'Amazon.co.uk price': row[5],
                'Amazon.de price': row[6],
                'Amazon.ca price': row[7],
            }
            past_searches.append(search)

    return past_searches