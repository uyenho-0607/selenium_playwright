from appium.webdriver.common.appiumby import AppiumBy
from framework.core.mobile_base_page import MobileBasePage


class IOSCalculatorPage(MobileBasePage):
    # iOS-specific locators
    DIGIT_BUTTON = "-ios predicate string:label == '{}' AND type == 'XCUIElementTypeButton'"
    PLUS_BUTTON = "-ios class chain:**/XCUIElementTypeButton[`label == \"+\"`]"
    EQUALS_BUTTON = "-ios class chain:**/XCUIElementTypeButton[`label == \"=\"`]"
    RESULT_FIELD = "-ios class chain:**/XCUIElementTypeStaticText[`label CONTAINS[cd] \"result\"`]"
    CLEAR_BUTTON = "-ios class chain:**/XCUIElementTypeButton[`label == \"C\"`]"
    ALL_CLEAR_BUTTON = "-ios class chain:**/XCUIElementTypeButton[`label == \"AC\"`]"

    def tap_digit(self, digit: int):
        """
        Tap a digit button
        :param digit: The digit to tap (0-9)
        """
        locator = self.DIGIT_BUTTON.format(digit)
        self.tap_element(AppiumBy.IOS_PREDICATE, locator)
        return self

    def tap_plus(self):
        """Tap the plus button"""
        self.tap_element(AppiumBy.IOS_CLASS_CHAIN, self.PLUS_BUTTON)
        return self

    def tap_equals(self):
        """Tap the equals button"""
        self.tap_element(AppiumBy.IOS_CLASS_CHAIN, self.EQUALS_BUTTON)
        return self

    def get_result(self) -> str:
        """Get the result value"""
        return self.get_text(AppiumBy.IOS_CLASS_CHAIN, self.RESULT_FIELD)

    def clear(self):
        """Clear the calculator"""
        self.tap_element(AppiumBy.IOS_CLASS_CHAIN, self.CLEAR_BUTTON)
        return self

    def all_clear(self):
        """All Clear - Reset calculator"""
        self.tap_element(AppiumBy.IOS_CLASS_CHAIN, self.ALL_CLEAR_BUTTON)
        return self

    def calculate_sum(self, a: int, b: int) -> str:
        """
        Calculate the sum of two numbers
        :param a: First number
        :param b: Second number
        :return: Result as string
        """
        self.all_clear()  # Start fresh
        
        # Convert numbers to digits and tap them
        for digit in str(a):
            self.tap_digit(int(digit))
        
        self.tap_plus()
        
        for digit in str(b):
            self.tap_digit(int(digit))
        
        self.tap_equals()
        return self.get_result()

    def perform_scientific_calculation(self):
        """
        Perform scientific calculation (iOS specific - requires rotation)
        """
        # Rotate to landscape for scientific mode
        self.driver.orientation = 'LANDSCAPE'
        # Add scientific calculation steps here
        self.driver.orientation = 'PORTRAIT'  # Return to portrait
        return self 