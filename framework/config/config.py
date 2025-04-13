import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Environment settings
    BASE_URL = os.getenv('BASE_URL', 'https://www.google.com')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'qa')
    BROWSER = os.getenv('BROWSER', 'chrome')
    HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'

    # Timeouts
    IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))
    EXPLICIT_WAIT = int(os.getenv('EXPLICIT_WAIT', '10'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))

    # Appium Settings
    APPIUM_HUB = os.getenv('APPIUM_HUB', 'http://localhost:4723/wd/hub')

    @staticmethod
    def get_android_capabilities() -> Dict[str, Any]:
        return {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'deviceName': os.getenv('ANDROID_DEVICE', 'Pixel_4_API_30'),
            'app': os.getenv('ANDROID_APP_PATH', ''),
            'noReset': False
        }

    @staticmethod
    def get_ios_capabilities() -> Dict[str, Any]:
        return {
            'platformName': 'iOS',
            'automationName': 'XCUITest',
            'deviceName': os.getenv('IOS_DEVICE', 'iPhone 12'),
            'platformVersion': os.getenv('IOS_VERSION', '14.5'),
            'app': os.getenv('IOS_APP_PATH', ''),
            'noReset': False
        }

    @staticmethod
    def get_playwright_config() -> Dict[str, Any]:
        return {
            'headless': Config.HEADLESS,
            'viewport': {'width': 1920, 'height': 1080},
            'timeout': Config.PAGE_LOAD_TIMEOUT * 1000,  # Convert to milliseconds
            'trace': 'retain-on-failure'
        }

    @staticmethod
    def get_selenium_options(browser: str) -> Dict[str, Any]:
        options = {
            'headless': Config.HEADLESS,
            'implicit_wait': Config.IMPLICIT_WAIT,
            'page_load_timeout': Config.PAGE_LOAD_TIMEOUT
        }
        if browser.lower() == 'chrome':
            options.update({
                'arguments': ['--start-maximized', '--disable-extensions']
            })
        return options 