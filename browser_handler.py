from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time

logger = logging.getLogger(__name__)

class BrowserHandler:
    """Handles headless browser operations for JavaScript-rendered pages"""
    
    def __init__(self):
        self.driver = None
    
    def initialize_driver(self):
        """Initialize headless Chrome browser"""
        try:
            import os
            chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
    
            chrome_options = Options()
            chrome_options.binary_location = chrome_bin
    
            # Required for headless mode inside Render containers
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--remote-debugging-port=9222")
    
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
    
            logger.info("Chrome driver initialized successfully")
            return True
    
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {str(e)}")
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
        except Exception as e:
            logger.error(f"Error fetching page content: {str(e)}")
            return None
    
    def get_text_content(self, url, selector="#result"):
        """
        Get text content from a specific element
        
        Args:
            url: URL to fetch
            selector: CSS selector for the element
        
        Returns:
            Text content of the element
        """
        try:
            if not self.driver:
                if not self.initialize_driver():
                    return None
            
            logger.info(f"Fetching text from {url} with selector {selector}")
            self.driver.get(url)
            
            # Wait for element
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            text_content = element.text
            logger.info("Text content extracted successfully")
            
            return text_content
        except Exception as e:
            logger.error(f"Error getting text content: {str(e)}")
            return None
    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
            finally:
                self.driver = None
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()

