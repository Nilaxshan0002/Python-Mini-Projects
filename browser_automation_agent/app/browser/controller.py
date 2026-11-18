from playwright.sync_api import sync_playwright
import base64
import logging

logger = logging.getLogger(__name__)

class BrowserController:
    def __init__(self, headless=False):
        logger.info("Initializing Playwright Browser...")
        self.playwright = sync_playwright().start()
        # Set headless=True for production, False to watch the agent work
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.page = self.context.new_page()

    def navigate(self, url: str) -> str:
        try:
            self.page.goto(url, wait_until="networkidle", timeout=15000)
            return f"Successfully navigated to {url}"
        except Exception as e:
            return f"Failed to navigate: {str(e)}"

    def get_screenshot(self) -> str:
        """Captures the screen and returns it as a base64 string."""
        screenshot_bytes = self.page.screenshot(full_page=False)
        return base64.b64encode(screenshot_bytes).decode('utf-8')

    def click(self, x: int, y: int) -> str:
        try:
            self.page.mouse.click(x, y)
            self.page.wait_for_timeout(1000) # Wait for UI to react
            return f"Clicked at coordinates ({x}, {y})"
        except Exception as e:
            return f"Failed to click: {str(e)}"

    def type_text(self, text: str) -> str:
        try:
            self.page.keyboard.type(text, delay=50) # Add slight delay to mimic human
            self.page.wait_for_timeout(500)
            return f"Typed text: '{text}'"
        except Exception as e:
            return f"Failed to type: {str(e)}"

    def scroll(self, direction: str) -> str:
        try:
            if direction.lower() == "down":
                self.page.mouse.wheel(0, 600)
            else:
                self.page.mouse.wheel(0, -600)
            self.page.wait_for_timeout(500)
            return f"Scrolled {direction}"
        except Exception as e:
            return f"Failed to scroll: {str(e)}"

    def press_key(self, key: str) -> str:
        try:
            self.page.keyboard.press(key)
            self.page.wait_for_timeout(500)
            return f"Pressed key: {key}"
        except Exception as e:
            return f"Failed to press key: {str(e)}"

    def close(self):
        logger.info("Closing Browser...")
        self.context.close()
        self.browser.close()
        self.playwright.stop()