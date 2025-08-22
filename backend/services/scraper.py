import httpx
from bs4 import BeautifulSoup
from typing import List,Dict

async def scrape_page(url: str, selectors: List[str]) -> Dict[str, List[str]]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    results = {}
    for selector in selectors:
        elements = soup.select(selector)
        results[selector] = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
    return results

def flatten_scraped_data(data: Dict[str, List[str]], url: str) -> List[Dict]:
    chunks = []
    for selector, texts in data.items():
        for text in texts:
            chunks.append({
                "text": f"[{selector}] {text}",
                "source": url,
                "page": selector  # optional: treat selector as pseudo-page
            })
    return chunks
