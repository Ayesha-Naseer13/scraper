import os
import re
import aiohttp
import asyncio
import csv
from bs4 import BeautifulSoup
from aiofiles import open as aio_open
from urllib.parse import urljoin

BASE_URL = "https://papers.nips.cc"
OUTPUT_DIR = "D:/scraper/papers"
METADATA_FILE = os.path.join(OUTPUT_DIR, "metadata.csv")
THREAD_COUNT = 10
MAX_RETRIES = 3
TIMEOUT = 120
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create a lock for CSV writing
csv_lock = asyncio.Lock()

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)[:200]

async def save_to_csv(data):
    """Async CSV writer with lock protection"""
    async with csv_lock:
        file_exists = os.path.exists(METADATA_FILE)
        async with aio_open(METADATA_FILE, mode="a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["year", "paper_url", "pdf_url", "title"])
            if not file_exists:
                await writer.writeheader()
            await writer.writerow(data)

async def fetch(session, url, retries=MAX_RETRIES):
    for attempt in range(1, retries + 1):
        try:
            async with session.get(url, timeout=TIMEOUT) as response:
                response.raise_for_status()
                return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == retries:
                print(f"Failed to fetch {url} after {retries} attempts: {e}")
                return None
            await asyncio.sleep(attempt * 2)
    return None

async def process_year(session, year_url, semaphore):
    html = await fetch(session, year_url)
    if not html:
        return

    # Extract year from URL
    try:
        year = int(year_url.split("/")[-1])
    except ValueError:
        print(f"Invalid year in URL: {year_url}")
        return

    soup = BeautifulSoup(html, "html.parser")
    paper_links = soup.select("ul.paper-list li a[href$='Abstract.html'], a[href$='.pdf']")
    print(f"Found {len(paper_links)} papers in {year_url}")
    
    tasks = [process_paper(session, urljoin(BASE_URL, link["href"]), year, semaphore) 
             for link in paper_links]
    await asyncio.gather(*tasks)

async def process_paper(session, paper_url, year, semaphore):
    html = await fetch(session, paper_url)
    if not html:
        return

    soup = BeautifulSoup(html, "html.parser")
    pdf_link = soup.select_one("a[href$='Paper.pdf'], a[href$='Paper-Conference.pdf']")
    
    if not pdf_link:
        return

    pdf_url = urljoin(BASE_URL, pdf_link["href"])
    title = soup.title.string.strip() if soup.title else "Untitled"
    filename = sanitize_filename(title) + ".pdf"

    # Prepare metadata
    metadata = {
        "year": year,
        "paper_url": paper_url,
        "pdf_url": pdf_url,
        "title": title
    }

    async with semaphore:
        # Save metadata first in case download fails
        await save_to_csv(metadata)
        await download_pdf(session, pdf_url, filename)

async def download_pdf(session, pdf_url, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        print(f"Skipping existing: {filename}")
        return

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.get(pdf_url, timeout=TIMEOUT) as response:
                if response.status == 200:
                    content = await response.read()
                    async with aio_open(filepath, "wb") as f:
                        await f.write(content)
                    print(f"Downloaded: {filepath}")
                    return
                print(f"HTTP {response.status} for {pdf_url}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == MAX_RETRIES:
                print(f"Failed to download {pdf_url} after {MAX_RETRIES} attempts: {e}")
                return
            await asyncio.sleep(attempt * 2)

async def main():
    headers = {'User-Agent': USER_AGENT}
    async with aiohttp.ClientSession(headers=headers) as session:
        html = await fetch(session, BASE_URL)
        if not html:
            return
        
        soup = BeautifulSoup(html, "html.parser")
        year_links = [urljoin(BASE_URL, link["href"]) 
                     for link in soup.select("a[href^='/paper_files/paper/'], a[href^='/book/']")]
        
        print(f"Found {len(year_links)} year archive links.")
        
        semaphore = asyncio.Semaphore(THREAD_COUNT)
        tasks = [process_year(session, link, semaphore) for link in year_links]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())