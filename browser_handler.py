# browser_handler.py
import os
import logging
from contextlib import contextmanager
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class BrowserHandler:
    """
    Simple synchronous Playwright browser handler.
    Usage:
        bh = BrowserHandler(headless=True)
        page = bh.new_page()
        page.goto("https://example.com")
        html = page.content()
        bh.screenshot(page, "out.png")
        bh.close()
    """

    def __init__(self, browser_name="chromium", headless=True, timeout=30_000):
        """
        browser_name: "chromium", "firefox" or "webkit" (chromium recommended)
        headless: boolean
        timeout: default timeout in milliseconds for waits/navigation
        """
        self.playwright = None
        self.browser = None
        self.browser_name = browser_name
        self.headless = headless
        self.timeout = timeout
        try:
            self.playwright = sync_playwright().start()
            if browser_name == "chromium":
                browser_launcher = self.playwright.chromium
            elif browser_name == "firefox":
                browser_launcher = self.playwright.firefox
            elif browser_name == "webkit":
                browser_launcher = self.playwright.webkit
            else:
                raise ValueError("browser_name must be one of: chromium, firefox, webkit")

            # You can pass additional launch options here (e.g., args)
            launch_args = {
                "headless": headless,
                # you can set slow_mo for debugging or pass args like ['--no-sandbox']
            }

            # If running in containers / PaaS, --no-sandbox is sometimes needed
            # Only add if necessary:
            if os.getenv("PLAYWRIGHT_ALLOW_NO_SANDBOX", "1") == "1":
                launch_args.setdefault("args", []).append("--no-sandbox")

            self.browser = browser_launcher.launch(**launch_args)
            logger.info(f"Started Playwright {browser_name} (headless={headless})")
        except Exception as e:
            logger.exception("Failed to start Playwright browser")
            # make sure to clean up partially-started resources
            self.close()
            raise

    def new_page(self, viewport={"width": 1280, "height": 800}, user_agent: str | None = None):
        """
        Returns a Playwright Page object.
        """
        context_args = {
            "viewport": viewport,
        }
        if user_agent:
            context_args["user_agent"] = user_agent

        context = self.browser.new_context(**context_args)
        page = context.new_page()
        page.set_default_navigation_timeout(self.timeout)
        page.set_default_timeout(self.timeout)
        return page

    def goto(self, page, url, wait_until="load"):
        """
        Navigate a page (wrapper)
        wait_until: "load", "domcontentloaded", "networkidle", or "commit"
        """
        return page.goto(url, wait_until=wait_until)

    def content(self, page):
        """Return page HTML"""
        return page.content()

    def screenshot(self, page, path=None, full_page=False):
        """
        Takes a screenshot. If `path` is None, returns bytes.
        """
        kwargs = {"full_page": full_page}
        if path:
            kwargs["path"] = path
            page.screenshot(**kwargs)
            return path
        else:
            return page.screenshot(**kwargs)

    def evaluate(self, page, expression, *args):
        """Run JS in page: expression can be a function (string) or JS string"""
        return page.evaluate(expression, *args)

    def wait_for_selector(self, page, selector, timeout=None):
        """
        Wait for selector and return element handle (or None on timeout)
        """
        try:
            return page.wait_for_selector(selector, timeout=timeout or self.timeout)
        except PlaywrightTimeoutError:
            return None

    def close(self):
        """Close browser and playwright"""
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
        except Exception:
            logger.exception("Error closing browser")
        finally:
            try:
                if self.playwright:
                    self.playwright.stop()
                    self.playwright = None
            except Exception:
                logger.exception("Error stopping Playwright")

    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()

