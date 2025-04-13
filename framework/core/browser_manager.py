from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from playwright.sync_api import sync_playwright
from appium import webdriver as appium_webdriver
from framework.config.config import Config


class BrowserManager:
    def __init__(self):
        self.config = Config
        self._driver = None
        self._playwright = None

    def get_driver(self, platform: str, browser: str = None, capabilities: Dict = None) -> Any:
        """
        Get driver instance based on platform and browser
        :param platform: 'web', 'android', 'ios'
        :param browser: Browser name for web platform
        :param capabilities: Additional capabilities
        :return: Driver instance
        """
        if platform == 'web':
            return self._get_web_driver(browser)
        elif platform == 'android':
            return self._get_android_driver(capabilities)
        elif platform == 'ios':
            return self._get_ios_driver(capabilities)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    def _get_web_driver(self, browser: str):
        """Get web driver instance"""
        browser = browser.lower() if browser else self.config.BROWSER.lower()
        
        if browser == 'chrome':
            options = webdriver.ChromeOptions()
            if self.config.HEADLESS:
                options.add_argument('--headless')
            options.add_argument('--start-maximized')
            return webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )
        elif browser == 'firefox':
            options = webdriver.FirefoxOptions()
            if self.config.HEADLESS:
                options.add_argument('--headless')
            return webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options
            )
        elif browser == 'playwright':
            self._playwright = sync_playwright().start()
            browser_type = self._playwright.chromium
            browser = browser_type.launch(**self.config.get_playwright_config())
            context = browser.new_context()
            return context.new_page()
        else:
            raise ValueError(f"Unsupported browser: {browser}")

    def _get_android_driver(self, capabilities: Optional[Dict] = None):
        """Get Android driver instance"""
        caps = self.config.get_android_capabilities()
        if capabilities:
            caps.update(capabilities)
        
        return appium_webdriver.Remote(
            command_executor=self.config.APPIUM_HUB,
            desired_capabilities=caps
        )

    def _get_ios_driver(self, capabilities: Optional[Dict] = None):
        """Get iOS driver instance"""
        caps = self.config.get_ios_capabilities()
        if capabilities:
            caps.update(capabilities)
        
        return appium_webdriver.Remote(
            command_executor=self.config.APPIUM_HUB,
            desired_capabilities=caps
        )

    def quit_driver(self, driver: Any):
        """Quit driver instance"""
        if hasattr(driver, 'quit'):
            driver.quit()
        
        if self._playwright:
            self._playwright.stop()
            self._playwright = None 