from typing import Union, Optional
from selenium.webdriver.remote.webdriver import WebDriver as SeleniumDriver
from selenium.webdriver.remote.webelement import WebElement as SeleniumElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from playwright.sync_api import Page as PlaywrightPage
from appium.webdriver import WebElement as AppiumElement
from framework.utils.soft_assert import SoftAssert


class BasePage:
    def __init__(self, driver: Union[SeleniumDriver, PlaywrightPage, None] = None):
        self.driver = driver
        self.soft_assert = SoftAssert()
        self._timeout = 10

    def find_element(self, by: str, value: str) -> Union[SeleniumElement, AppiumElement, PlaywrightPage]:
        """
        Find an element using the appropriate method based on the driver type
        """
        if isinstance(self.driver, PlaywrightPage):
            return self.driver.locator(f"{by}={value}")
        else:  # Selenium or Appium
            return self.driver.find_element(by, value)

    def click(self, by: str, value: str):
        """
        Click an element using the appropriate method based on the driver type
        """
        if isinstance(self.driver, PlaywrightPage):
            self.driver.locator(f"{by}={value}").click()
        else:  # Selenium or Appium
            element = WebDriverWait(self.driver, self._timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            element.click()

    def type_text(self, by: str, value: str, text: str):
        """
        Type text into an element using the appropriate method based on the driver type
        """
        if isinstance(self.driver, PlaywrightPage):
            self.driver.locator(f"{by}={value}").fill(text)
        else:  # Selenium or Appium
            element = WebDriverWait(self.driver, self._timeout).until(
                EC.presence_of_element_located((by, value))
            )
            element.clear()
            element.send_keys(text)

    def get_text(self, by: str, value: str) -> str:
        """
        Get text from an element using the appropriate method based on the driver type
        """
        if isinstance(self.driver, PlaywrightPage):
            return self.driver.locator(f"{by}={value}").text_content()
        else:  # Selenium or Appium
            element = WebDriverWait(self.driver, self._timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element.text

    def is_element_visible(self, by: str, value: str) -> bool:
        """
        Check if an element is visible using the appropriate method based on the driver type
        """
        try:
            if isinstance(self.driver, PlaywrightPage):
                return self.driver.locator(f"{by}={value}").is_visible()
            else:  # Selenium or Appium
                element = WebDriverWait(self.driver, self._timeout).until(
                    EC.visibility_of_element_located((by, value))
                )
                return element.is_displayed()
        except:
            return False 