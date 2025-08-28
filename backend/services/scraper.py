# backend/services/scraper.py
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import asyncio
from urllib.parse import urlparse

class WebScraper:
    """
    A class for scraping web pages and extracting structured content.
    """
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        user_agent: Optional[str] = None,
        default_selectors: Optional[List[str]] = None
    ):
        """
        Initialize the WebScraper.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            user_agent: Custom user agent string
            default_selectors: Default CSS selectors to use if none provided
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.default_selectors = default_selectors or ["p", "h1", "h2", "h3", "li", "article", "section"]
        self.logger = logging.getLogger(__name__)
    
    async def _make_request(self, url: str, client: httpx.AsyncClient) -> Optional[httpx.Response]:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: URL to request
            client: HTTPX async client
            
        Returns:
            Response object or None if failed
        """
        headers = {"User-Agent": self.user_agent}
        
        for attempt in range(self.max_retries):
            try:
                response = await client.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    follow_redirects=True
                )
                response.raise_for_status()
                return response
                
            except httpx.HTTPStatusError as e:
                self.logger.warning(f"⚠️ HTTP error {e.response.status_code} for {url} (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
            except httpx.RequestError as e:
                self.logger.warning(f"⚠️ Request error for {url}: {e} (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    async def scrape_page(
        self,
        url: str,
        selectors: Optional[List[str]] = None,
        extract_links: bool = False,
        extract_images: bool = False
    ) -> Dict[str, List[str]]:
        """
        Scrape a web page and extract content based on CSS selectors.
        
        Args:
            url: URL to scrape
            selectors: CSS selectors for content extraction
            extract_links: Whether to extract links
            extract_images: Whether to extract image information
            
        Returns:
            Dictionary with selector keys and extracted content lists
        """
        selectors = selectors or self.default_selectors
        results = {}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await self._make_request(url, client)
                
                if response is None:
                    self.logger.error(f"❌ Failed to fetch URL: {url}")
                    return {}
                
                soup = BeautifulSoup(response.text, "lxml")
                
                # Extract content based on selectors
                for selector in selectors:
                    try:
                        elements = soup.select(selector)
                        texts = [
                            el.get_text(strip=True) 
                            for el in elements 
                            if el.get_text(strip=True)
                        ]
                        results[selector] = texts
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to extract with selector '{selector}': {e}")
                        results[selector] = []
                
                # Extract links if requested
                if extract_links:
                    results["links"] = self._extract_links(soup, url)
                
                # Extract images if requested
                if extract_images:
                    results["images"] = self._extract_images(soup, url)
                
                # Extract page metadata
                results["metadata"] = self._extract_metadata(soup, url)
                
                self.logger.info(f"✅ Successfully scraped {url}: {sum(len(v) for v in results.values())} elements")
                return results
                
        except Exception as e:
            self.logger.error(f"❌ Failed to scrape {url}: {e}")
            return {}
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Extract all links from the page.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of link information dictionaries
        """
        links = []
        for link in soup.find_all("a", href=True):
            try:
                href = link["href"]
                # Resolve relative URLs
                if href.startswith("/"):
                    parsed_base = urlparse(base_url)
                    href = f"{parsed_base.scheme}://{parsed_base.netloc}{href}"
                elif href.startswith("#") or href.startswith("javascript:"):
                    continue
                
                links.append({
                    "text": link.get_text(strip=True),
                    "url": href,
                    "title": link.get("title", "")
                })
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to extract link: {e}")
                continue
        
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Extract all images from the page.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative image URLs
            
        Returns:
            List of image information dictionaries
        """
        images = []
        for img in soup.find_all("img", src=True):
            try:
                src = img["src"]
                # Resolve relative URLs
                if src.startswith("/"):
                    parsed_base = urlparse(base_url)
                    src = f"{parsed_base.scheme}://{parsed_base.netloc}{src}"
                
                images.append({
                    "src": src,
                    "alt": img.get("alt", ""),
                    "title": img.get("title", ""),
                    "width": img.get("width"),
                    "height": img.get("height")
                })
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to extract image: {e}")
                continue
        
        return images
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract page metadata.
        
        Args:
            soup: BeautifulSoup object
            url: Page URL
            
        Returns:
            Dictionary of metadata
        """
        metadata = {"url": url}
        
        # Title
        title = soup.find("title")
        if title:
            metadata["title"] = title.get_text(strip=True)
        
        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            metadata["description"] = meta_desc["content"]
        
        # Meta keywords
        meta_keywords = soup.find("meta", attrs={"name": "keywords"})
        if meta_keywords and meta_keywords.get("content"):
            metadata["keywords"] = meta_keywords["content"]
        
        # Open Graph metadata
        og_properties = ["title", "description", "image", "url", "type"]
        for prop in og_properties:
            og_tag = soup.find("meta", attrs={"property": f"og:{prop}"})
            if og_tag and og_tag.get("content"):
                metadata[f"og_{prop}"] = og_tag["content"]
        
        return metadata
    
    def flatten_scraped_data(self, data: Dict[str, List[str]], url: str) -> List[Dict]:
        """
        Convert scraped data into a format suitable for chunking and indexing.
        
        Args:
            data: Scraped data dictionary
            url: Source URL
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        for selector, texts in data.items():
            # Skip non-content keys
            if selector in ["links", "images", "metadata"]:
                continue
                
            for i, text in enumerate(texts):
                if text:  # Only add non-empty text
                    chunks.append({
                        "text": text,
                        "source": url,
                        "selector": selector,
                        "chunk_id": f"{url}_{selector}_{i}",
                        "type": "web_content"
                    })
        
        # Add metadata as a separate chunk
        if "metadata" in data:
            metadata = data["metadata"]
            chunks.append({
                "text": f"Page Metadata: {metadata.get('title', 'No title')} - {metadata.get('description', 'No description')}",
                "source": url,
                "selector": "metadata",
                "chunk_id": f"{url}_metadata",
                "type": "metadata"
            })
        
        self.logger.info(f"📊 Flattened {len(chunks)} chunks from {url}")
        return chunks
    
    async def scrape_multiple_pages(
        self,
        urls: List[str],
        selectors: Optional[List[str]] = None,
        concurrency: int = 3
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        Scrape multiple pages concurrently.
        
        Args:
            urls: List of URLs to scrape
            selectors: CSS selectors for content extraction
            concurrency: Maximum number of concurrent requests
            
        Returns:
            Dictionary mapping URLs to their scraped data
        """
        semaphore = asyncio.Semaphore(concurrency)
        results = {}
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                data = await self.scrape_page(url, selectors)
                return url, data
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in completed:
            if isinstance(result, Exception):
                self.logger.error(f"❌ Failed to scrape URL in batch: {result}")
                continue
            url, data = result
            results[url] = data
        
        return results
    
    def update_parameters(
        self,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        user_agent: Optional[str] = None,
        default_selectors: Optional[List[str]] = None
    ) -> None:
        """
        Update scraper parameters.
        
        Args:
            timeout: New request timeout
            max_retries: New maximum retries
            user_agent: New user agent
            default_selectors: New default selectors
        """
        if timeout is not None:
            self.timeout = timeout
        if max_retries is not None:
            self.max_retries = max_retries
        if user_agent is not None:
            self.user_agent = user_agent
        if default_selectors is not None:
            self.default_selectors = default_selectors
        
        self.logger.info(f"🔄 Updated scraper parameters: timeout={self.timeout}, retries={self.max_retries}")

        
# import httpx
# from bs4 import BeautifulSoup
# from typing import List,Dict

# async def scrape_page(url: str, selectors: List[str]) -> Dict[str, List[str]]:
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url)
#         response.raise_for_status()

#     soup = BeautifulSoup(response.text, "lxml")
#     results = {}
#     for selector in selectors:
#         elements = soup.select(selector)
#         results[selector] = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
#     return results

# def flatten_scraped_data(data: Dict[str, List[str]], url: str) -> List[Dict]:
#     chunks = []
#     for selector, texts in data.items():
#         for text in texts:
#             chunks.append({
#                 "text": f"[{selector}] {text}",
#                 "source": url,
#                 "page": selector  # optional: treat selector as pseudo-page
#             })
#     return chunks
