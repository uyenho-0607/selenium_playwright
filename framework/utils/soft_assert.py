from typing import List, Any, Callable
import traceback
from assertpy import assert_that


class SoftAssert:
    def __init__(self):
        self._errors: List[str] = []
        self._current_test: str = ""

    def assert_that(self, value: Any) -> 'assertpy.AssertionBuilder':
        """
        Creates an assertion builder for soft assertions
        :param value: The value to assert
        :return: AssertionBuilder instance
        """
        try:
            return assert_that(value)
        except AssertionError as e:
            self._errors.append(f"{str(e)}\n{traceback.format_exc()}")
            return assert_that(value)

    def assert_true(self, condition: bool, message: str = None):
        """
        Assert that a condition is True
        :param condition: The condition to check
        :param message: Optional custom message
        """
        try:
            assert_that(condition).is_true()
        except AssertionError as e:
            error_message = message if message else str(e)
            self._errors.append(f"{error_message}\n{traceback.format_exc()}")

    def assert_false(self, condition: bool, message: str = None):
        """
        Assert that a condition is False
        :param condition: The condition to check
        :param message: Optional custom message
        """
        try:
            assert_that(condition).is_false()
        except AssertionError as e:
            error_message = message if message else str(e)
            self._errors.append(f"{error_message}\n{traceback.format_exc()}")

    def assert_equals(self, actual: Any, expected: Any, message: str = None):
        """
        Assert that two values are equal
        :param actual: The actual value
        :param expected: The expected value
        :param message: Optional custom message
        """
        try:
            assert_that(actual).is_equal_to(expected)
        except AssertionError as e:
            error_message = message if message else str(e)
            self._errors.append(f"{error_message}\n{traceback.format_exc()}")

    def verify_all(self):
        """
        Verifies all assertions and raises AssertionError if any failed
        """
        if self._errors:
            raise AssertionError("\n".join(self._errors))

    def reset(self):
        """
        Resets the soft assert instance
        """
        self._errors = [] 