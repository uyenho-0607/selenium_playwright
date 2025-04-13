import pytest
import allure
from framework.pages.web.google_page import GooglePage


@allure.feature("Search Functionality")
class TestGoogleSearch:
    
    @allure.story("Search with Selenium")
    @pytest.mark.web
    def test_google_search_selenium(self, selenium_driver):
        google_page = GooglePage(selenium_driver)
        
        with allure.step("Navigate to Google"):
            google_page.navigate()
        
        with allure.step("Perform search"):
            google_page.search("Selenium with Python")
        
        with allure.step("Verify search results"):
            google_page.soft_assert.assert_true(
                google_page.is_element_visible(*GooglePage.FIRST_RESULT),
                "Search results should be visible"
            )
            first_result = google_page.get_first_result_text()
            google_page.soft_assert.assert_that(first_result).contains("Selenium")
            google_page.soft_assert.verify_all()

    @allure.story("Search with Playwright")
    @pytest.mark.web
    def test_google_search_playwright(self, playwright_page):
        google_page = GooglePage(playwright_page)
        
        with allure.step("Navigate to Google"):
            google_page.navigate()
        
        with allure.step("Perform search"):
            google_page.search("Playwright with Python")
        
        with allure.step("Verify search results"):
            google_page.soft_assert.assert_true(
                google_page.is_element_visible(*GooglePage.FIRST_RESULT),
                "Search results should be visible"
            )
            first_result = google_page.get_first_result_text()
            google_page.soft_assert.assert_that(first_result).contains("Playwright")
            google_page.soft_assert.verify_all() 