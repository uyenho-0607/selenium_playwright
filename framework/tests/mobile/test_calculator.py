import pytest
import allure
from framework.pages.mobile.calculator_page import CalculatorPage


@allure.feature("Calculator")
class TestCalculator:
    
    @allure.story("Basic Calculations")
    @pytest.mark.mobile
    @pytest.mark.android
    def test_addition(self, android_driver):
        calculator = CalculatorPage(android_driver)
        
        with allure.step("Clear calculator"):
            calculator.clear()
        
        with allure.step("Calculate 5 + 3"):
            result = calculator.calculate_sum(5, 3)
        
        with allure.step("Verify result"):
            calculator.soft_assert.assert_equals(result, "8", "Addition result should be 8")
            calculator.soft_assert.verify_all()

    @allure.story("Calculator UI")
    @pytest.mark.mobile
    @pytest.mark.android
    def test_calculator_ui_interactions(self, android_driver):
        calculator = CalculatorPage(android_driver)
        
        with allure.step("Clear calculator"):
            calculator.clear()
        
        with allure.step("Test long press on clear button"):
            calculator.long_press(AppiumBy.XPATH, calculator.CLEAR_BUTTON)
            calculator.soft_assert.assert_equals(
                calculator.get_result(), 
                "0",
                "Display should be cleared after long press"
            )
        
        with allure.step("Test swipe on result field"):
            calculator.swipe_element(
                AppiumBy.XPATH,
                calculator.RESULT_FIELD,
                "left"
            )
        
        with allure.step("Verify all assertions"):
            calculator.soft_assert.verify_all()

    @allure.story("Calculator Gestures")
    @pytest.mark.mobile
    @pytest.mark.android
    def test_calculator_gestures(self, android_driver):
        calculator = CalculatorPage(android_driver)
        
        with allure.step("Clear calculator"):
            calculator.clear()
        
        with allure.step("Enter numbers using tap gestures"):
            # Tap multiple digits in sequence
            calculator.tap_digit(1)
            calculator.tap_digit(2)
            calculator.tap_digit(3)
            
            current_value = calculator.get_result()
            calculator.soft_assert.assert_equals(
                current_value,
                "123",
                "Tapped digits should appear in sequence"
            )
        
        with allure.step("Test pull to refresh"):
            calculator.pull_to_refresh()
            calculator.soft_assert.assert_equals(
                calculator.get_result(),
                "0",
                "Display should be cleared after pull to refresh"
            )
        
        with allure.step("Verify all assertions"):
            calculator.soft_assert.verify_all() 