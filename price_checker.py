import requests
from bs4 import BeautifulSoup
import re

class PriceChecker:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_price(self, url):
        """Attempt to fetch price from a URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try common price patterns
            price = self._extract_price_amazon(soup, url)
            if not price:
                price = self._extract_price_generic(soup)
            
            return price
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    
    def _extract_price_amazon(self, soup, url):
        """Extract price from Amazon"""
        if 'amazon' not in url.lower():
            return None
        
        # Amazon-specific selectors
        selectors = [
            '.a-price-whole',
            '#priceblock_ourprice',
            '#priceblock_dealprice',
            '.a-price .a-offscreen'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text()
                return self._parse_price(price_text)
        
        return None
    
    def _extract_price_generic(self, soup):
        """Generic price extraction"""
        # Look for common price patterns
        price_patterns = [
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'£\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'€\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|GBP|EUR)'
        ]
        
        text = soup.get_text()
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                return self._parse_price(match.group(1))
        
        return None
    
    # Replaced bare except with specific exception handling

    def _parse_price(self, price_text):
        """Parse price string to float"""
        try:
            # Remove currency symbols and commas
            clean_price = re.sub(r'[^\d.]', '', price_text)
            return float(clean_price)
        except ValueError:
            # Handle cases where conversion to float fails
            return None

    def fetch_image_url(self, url):
        """Fetch main product image from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try Open Graph image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return og_image['content']
            
            # Try Twitter card image
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                return twitter_image['content']
            
            # Try first large image
            images = soup.find_all('img')
            for img in images:
                src = img.get('src') or img.get('data-src')
                if src and ('http' in src):
                    width = img.get('width')
                    if width and int(width) > 200:
                        return src
        except requests.RequestException as e:
            # Handle HTTP-related exceptions
            print(f"Error fetching image URL: {e}")
        except Exception as e:
            # Catch other unexpected exceptions
            print(f"Unexpected error: {e}")
        return None