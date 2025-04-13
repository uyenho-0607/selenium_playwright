from appium.webdriver.common.appiumby import AppiumBy
from framework.core.mobile_base_page import MobileBasePage


class CalculatorPage(MobileBasePage):
    # Locators
    DIGIT_BUTTON = "(//android.widget.Button[contains(@resource-id, 'digit_{}')])"
    PLUS_BUTTON = "//android.widget.Button[contains(@resource-id, 'op_add')]"
    EQUALS_BUTTON = "//android.widget.Button[contains(@resource-id, 'eq')]"
    RESULT_FIELD = "//android.widget.TextView[contains(@resource-id, 'result')]"
    CLEAR_BUTTON = "//android.widget.Button[contains(@resource-id, 'clr')]"

    def tap_digit(self, digit: int):
        """
        Tap a digit button
        :param digit: The digit to tap (0-9)
        """
        locator = self.DIGIT_BUTTON.format(digit)
        self.tap_element(AppiumBy.XPATH, locator)
        return self

    def tap_plus(self):
        """Tap the plus button"""
        self.tap_element(AppiumBy.XPATH, self.PLUS_BUTTON)
        return self

    def tap_equals(self):
        """Tap the equals button"""
        self.tap_element(AppiumBy.XPATH, self.EQUALS_BUTTON)
        return self

    def get_result(self) -> str:
        """Get the result value"""
        return self.get_text(AppiumBy.XPATH, self.RESULT_FIELD)

    def clear(self):
        """Clear the calculator"""
        self.tap_element(AppiumBy.XPATH, self.CLEAR_BUTTON)
        return self

    def calculate_sum(self, a: int, b: int) -> str:
        """
        Calculate the sum of two numbers
        :param a: First number
        :param b: Second number
        :return: Result as string
        """
        # Convert numbers to digits and tap them
        for digit in str(a):
            self.tap_digit(int(digit))
        
        self.tap_plus()
        
        for digit in str(b):
            self.tap_digit(int(digit))
        
        self.tap_equals()
        return self.get_result() 