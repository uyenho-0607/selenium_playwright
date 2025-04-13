from selenium.webdriver.common.by import By
from framework.core.base_page import BasePage


class GooglePage(BasePage):
    # Locators
    SEARCH_INPUT = (By.NAME, "q")
    SEARCH_BUTTON = (By.NAME, "btnK")
    FIRST_RESULT = (By.CSS_SELECTOR, "div.g h3")

    def navigate(self):
        """
        Navigate to Google homepage
        """
        if hasattr(self.driver, 'goto'):  # Playwright
            self.driver.goto('https://www.google.com')
        else:  # Selenium/Appium
            self.driver.get('https://www.google.com')
        return self

    def search(self, query: str):
        """
        Perform a search
        """
        self.type_text(*self.SEARCH_INPUT, query)
        self.click(*self.SEARCH_BUTTON)
        return self

    def get_first_result_text(self) -> str:
        """
        Get the text of the first search result
        """
        return self.get_text(*self.FIRST_RESULT) 