from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import shutil
import os
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

class BrowserHandler:
    """Handles headless browser operations for JavaScript-rendered pages"""
    
    def __init__(self):
        self.driver = None
    
    def initialize_driver(self):
        """Initialize headless Chrome browser using the system chromedriver."""
        try:
            chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/chromium")

            # Debug info
            logger.info(
                "Using system chromedriver at /usr/bin/chromedriver, CHROME_BIN=%s, which chromium=%s",
                chrome_bin, shutil.which("chromium") or shutil.which("chromium-browser")
            )

            chrome_options = Options()
            chrome_options.binary_location = chrome_bin

            # Headless and container-friendly flags
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--remote-debugging-port=9222")

            # Use the system-installed chromedriver binary
            service = Service("/usr/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(5)

            logger.info("Chrome driver initialized successfully (system chromedriver)")
            return True

        except Exception:
            logger.exception("Failed to initialize Chrome driver (system chromedriver)")
            try:
                if self.driver:
                    self.driver.quit()
            except Exception:
                pass
            self.driver = None
            return False

    def fetch_page_content(self, url, wait_time=5):
        """
        Fetch content from a JavaScript-rendered page
        
        Args:
            url: URL to fetch
            wait_time: Time to wait for page to load (seconds)
        
        Returns:
            Rendered HTML content
        """
        try:
            if not self.driver:
                if not self.initialize_driver():
                    return None
            
            logger.info(f"Fetching URL: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(wait_time)
            
            # Wait for result div if it exists
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "result"))
                )
            except:
                logger.warning("No #result element found, proceeding with page source")
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            logger.info("Page content fetched successfully")
            
            return page_source
        except Exception:
            logger.exception("Error fetching page content")
            return None
    

    def get_text_content(self, url, selector="#result", wait_seconds=10):
        """
        Get text content from a specific element. Falls back to parsing page_source.
        """
        try:
            if not self.driver:
                if not self.initialize_driver():
                    return None
    
            logger.info(f"Fetching text from {url} with selector {selector}")
            self.driver.get(url)
    
            try:
                element = WebDriverWait(self.driver, wait_seconds).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                text_content = element.text
                logger.info("Text content extracted successfully (by selector)")
                return text_content
    
            except TimeoutException:
                logger.warning("Selector %s not found after %s seconds — falling back to page_source", selector, wait_seconds)
                # Option A: try a few common fallback selectors
                for alt in ["#result", ".result", ".content", "body"]:
                    try:
                        el = self.driver.find_element(By.CSS_SELECTOR, alt)
                        logger.info("Found content with fallback selector %s", alt)
                        return el.text
                    except Exception:
                        pass
    
                # Option B: parse page_source with BeautifulSoup
                page = self.driver.page_source
                soup = BeautifulSoup(page, "html.parser")
    
                # try to extract main text: look for main/article/div with text
                candidates = soup.select("main, article, .content, #content, body, div")
                for c in candidates:
                    text = c.get_text(separator="\n", strip=True)
                    if text and len(text) > 20:  # adjust threshold as needed
                        logger.info("Extracted text from page_source fallback (len=%s)", len(text))
                        return text
    
                logger.warning("No usable text found in fallback parsing")
                return None
    
        except Exception:
            logger.exception("Error getting text content")
            return None

    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception:
                logger.exception("Error closing browser")
            finally:
                self.driver = None
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()

