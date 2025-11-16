from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import sys
from bs4 import BeautifulSoup
import os
from pathlib import Path
from collections import deque
import re
import random
from limits import RateLimitItemPerSecond
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter

URL_prefix = "https://pl.wikipedia.org/"
CURRENT_PATH = current_path = Path(__file__).parent

MAX_DEPTH = 5
MAX_LINKS = 3

# Rate limiter
storage = MemoryStorage()
rate_limit = RateLimitItemPerSecond(10)  # 10 stron na 1 sekundę
limiter = FixedWindowRateLimiter(storage)

# Crawler ma pobierać:
# URL strony
# Tytuł (<title> lub <h1>)
# Tekst treści (bez menu, stopki, reklam)
# Lista linków dalej (maks 5 głębokości)

def save_web_content(soup, URL, title):
    content = soup.find("div", {"id": "mw-content-text"})

    for tag in content.find_all(["table", "style", "script", "sup"]):
        tag.decompose()

    text = content.get_text(separator=" ")
    text = " ".join(text.split()) 
    title = re.sub(r'[\\/*?:"<>|]', "", title)

    with open(os.path.join(DATA_PATH, title + ".txt"), "w", encoding="utf-8") as f:
        f.write(text)

def crawl(URL):
    visited = set()
    queue = deque([(URL, 0)])   # (adres, głębokość)

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    try:
        while queue:
            url, depth = queue.popleft()

            if url in visited:
                continue
            visited.add(url)

            if not limiter.test(rate_limit):
                time.sleep(2)
            limiter.hit(rate_limit)
            
            print(f"Głębokość: {depth}, URL: {url}")
            print("Długość kolejki:", len(queue))

            driver.get(url)
            driver.implicitly_wait(0.5)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            save_web_content(soup, url, driver.title)

            download_count = 0
            if depth < MAX_DEPTH:
                links = soup.select("#mw-content-text a[href^='/wiki/']")
                random.shuffle(links)
                for a in links:
                    if download_count >= MAX_LINKS:
                        break

                    queue.append((URL_prefix + a['href'], depth + 1))
                    download_count += 1
    finally:
        driver.quit()

def main():
    URL_sufix = "/wiki/" + input(f"Podaj adres strony ('x' aby zakończyć):\n{URL_prefix}wiki/")

    if URL_sufix[6] == 'x':
        sys.exit(2)
    
    
    DATA_PATH.mkdir(parents=True, exist_ok=True)    

    # Czyszczenie plików z ostatniego szukania
    for filename in os.listdir(DATA_PATH):
        file_path = os.path.join(DATA_PATH, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    URL = URL_prefix + URL_sufix

    crawl(URL)

if __name__ == "__main__":
    main()