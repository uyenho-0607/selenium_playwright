from typing import Optional, Tuple, Union, List, Dict
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from framework.core.base_page import BasePage
import time


class MobileBasePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.touch_action = TouchAction(self.driver)

    def tap_element(self, by: str, value: str, duration: int = 500):
        """
        Tap on an element
        :param by: Locator type
        :param value: Locator value
        :param duration: Tap duration in milliseconds
        """
        element = self.find_element(by, value)
        self.touch_action.tap(element, duration=duration).perform()

    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 500):
        """
        Swipe from one point to another
        :param start_x: Starting x-coordinate
        :param start_y: Starting y-coordinate
        :param end_x: Ending x-coordinate
        :param end_y: Ending y-coordinate
        :param duration: Swipe duration in milliseconds
        """
        self.touch_action.press(x=start_x, y=start_y)\
            .wait(duration)\
            .move_to(x=end_x, y=end_y)\
            .release()\
            .perform()

    def swipe_element(self, element_by: str, element_value: str, direction: str, percent: float = 0.5):
        """
        Swipe on an element in a specific direction
        :param element_by: Element locator type
        :param element_value: Element locator value
        :param direction: Direction to swipe ('up', 'down', 'left', 'right')
        :param percent: Percentage of element size to swipe
        """
        element = self.find_element(element_by, element_value)
        rect = element.rect
        start_x = rect['x'] + rect['width'] // 2
        start_y = rect['y'] + rect['height'] // 2

        if direction == 'up':
            end_x = start_x
            end_y = start_y - int(rect['height'] * percent)
        elif direction == 'down':
            end_x = start_x
            end_y = start_y + int(rect['height'] * percent)
        elif direction == 'left':
            end_x = start_x - int(rect['width'] * percent)
            end_y = start_y
        else:  # right
            end_x = start_x + int(rect['width'] * percent)
            end_y = start_y

        self.swipe(start_x, start_y, end_x, end_y)

    def scroll_to_text(self, text: str, direction: str = 'down', max_swipes: int = 10):
        """
        Scroll until text is found
        :param text: Text to find
        :param direction: Direction to scroll ('up' or 'down')
        :param max_swipes: Maximum number of swipes
        :return: True if text is found, False otherwise
        """
        for _ in range(max_swipes):
            try:
                element = self.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                         f'new UiSelector().textContains("{text}")')
                return True
            except NoSuchElementException:
                screen_size = self.driver.get_window_size()
                start_x = screen_size['width'] // 2
                start_y = screen_size['height'] * 0.8 if direction == 'up' else screen_size['height'] * 0.2
                end_y = screen_size['height'] * 0.2 if direction == 'up' else screen_size['height'] * 0.8
                self.swipe(start_x, start_y, start_x, end_y)
        return False

    def long_press(self, by: str, value: str, duration: int = 1000):
        """
        Long press on an element
        :param by: Locator type
        :param value: Locator value
        :param duration: Press duration in milliseconds
        """
        element = self.find_element(by, value)
        self.touch_action.long_press(element, duration=duration).release().perform()

    def pinch(self, by: str, value: str, scale: float = 0.5):
        """
        Pinch element (zoom out)
        :param by: Locator type
        :param value: Locator value
        :param scale: Scale factor (0-1)
        """
        element = self.find_element(by, value)
        rect = element.rect
        center_x = rect['x'] + rect['width'] // 2
        center_y = rect['y'] + rect['height'] // 2
        
        finger1 = TouchAction(self.driver)
        finger2 = TouchAction(self.driver)
        
        finger1.press(x=center_x + 50, y=center_y + 50)\
            .move_to(x=center_x + int(50 * scale), y=center_y + int(50 * scale))\
            .release()
        
        finger2.press(x=center_x - 50, y=center_y - 50)\
            .move_to(x=center_x - int(50 * scale), y=center_y - int(50 * scale))\
            .release()
        
        self.driver.multi_action(finger1, finger2).perform()

    def zoom(self, by: str, value: str, scale: float = 2.0):
        """
        Zoom element (zoom in)
        :param by: Locator type
        :param value: Locator value
        :param scale: Scale factor (>1)
        """
        element = self.find_element(by, value)
        rect = element.rect
        center_x = rect['x'] + rect['width'] // 2
        center_y = rect['y'] + rect['height'] // 2
        
        finger1 = TouchAction(self.driver)
        finger2 = TouchAction(self.driver)
        
        finger1.press(x=center_x + 50, y=center_y + 50)\
            .move_to(x=center_x + int(50 * scale), y=center_y + int(50 * scale))\
            .release()
        
        finger2.press(x=center_x - 50, y=center_y - 50)\
            .move_to(x=center_x - int(50 * scale), y=center_y - int(50 * scale))\
            .release()
        
        self.driver.multi_action(finger1, finger2).perform()

    def hide_keyboard(self):
        """Hide the keyboard if visible"""
        try:
            self.driver.hide_keyboard()
        except:
            pass

    def switch_context(self, context_name: Optional[str] = None):
        """
        Switch between native and webview contexts
        :param context_name: Context name to switch to, if None will switch to WEBVIEW
        """
        if context_name is None:
            # Find the first WEBVIEW context
            contexts = self.driver.contexts
            webview_contexts = [c for c in contexts if 'WEBVIEW' in c]
            if webview_contexts:
                self.driver.switch_to.context(webview_contexts[0])
        else:
            self.driver.switch_to.context(context_name)

    def switch_to_native(self):
        """Switch to native context"""
        self.driver.switch_to.context('NATIVE_APP')

    def get_element_location(self, by: str, value: str) -> Tuple[int, int]:
        """
        Get element's center coordinates
        :return: Tuple of (x, y) coordinates
        """
        element = self.find_element(by, value)
        rect = element.rect
        return (rect['x'] + rect['width'] // 2, rect['y'] + rect['height'] // 2)

    def pull_to_refresh(self):
        """Perform pull to refresh gesture"""
        screen_size = self.driver.get_window_size()
        start_x = screen_size['width'] // 2
        start_y = screen_size['height'] * 0.2
        end_y = screen_size['height'] * 0.8
        self.swipe(start_x, start_y, start_x, end_y, duration=1000)

    def draw_pattern(self, points: List[Tuple[int, int]], duration: int = 1000):
        """
        Draw a pattern by connecting points
        :param points: List of (x, y) coordinates to connect
        :param duration: Total duration of the pattern drawing
        """
        if len(points) < 2:
            return

        action = TouchAction(self.driver)
        point_duration = duration // (len(points) - 1)
        
        # Start at first point
        action.press(x=points[0][0], y=points[0][1]).wait(100)
        
        # Move through remaining points
        for point in points[1:]:
            action.move_to(x=point[0], y=point[1]).wait(point_duration)
        
        action.release().perform()

    def draw_circle(self, center_x: int, center_y: int, radius: int, duration: int = 1000):
        """
        Draw a circle gesture
        :param center_x: Circle center x-coordinate
        :param center_y: Circle center y-coordinate
        :param radius: Circle radius
        :param duration: Duration of the circle drawing
        """
        import math
        points = []
        steps = 36  # Number of points to make the circle
        
        for i in range(steps + 1):
            angle = 2 * math.pi * i / steps
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((int(x), int(y)))
        
        self.draw_pattern(points, duration)

    def rotate_element(self, by: str, value: str, degrees: int = 90, duration: int = 1000):
        """
        Rotate an element using two-finger gesture
        :param by: Locator type
        :param value: Locator value
        :param degrees: Degrees to rotate (positive for clockwise)
        :param duration: Duration of rotation
        """
        element = self.find_element(by, value)
        rect = element.rect
        center_x = rect['x'] + rect['width'] // 2
        center_y = rect['y'] + rect['height'] // 2
        radius = min(rect['width'], rect['height']) // 4

        import math
        angle_rad = math.radians(degrees)
        
        # Create two-finger rotation
        f1 = TouchAction(self.driver)
        f2 = TouchAction(self.driver)
        
        # First finger
        f1.press(x=center_x + radius, y=center_y)\
            .wait(duration)\
            .move_to(x=int(center_x + radius * math.cos(angle_rad)),
                    y=int(center_y + radius * math.sin(angle_rad)))\
            .release()
        
        # Second finger (opposite side)
        f2.press(x=center_x - radius, y=center_y)\
            .wait(duration)\
            .move_to(x=int(center_x - radius * math.cos(angle_rad)),
                    y=int(center_y - radius * math.sin(angle_rad)))\
            .release()
        
        MultiAction(self.driver).add(f1).add(f2).perform()

    def shake_element(self, by: str, value: str, intensity: float = 1.0):
        """
        Shake an element left and right
        :param by: Locator type
        :param value: Locator value
        :param intensity: Shake intensity multiplier
        """
        element = self.find_element(by, value)
        rect = element.rect
        center_x = rect['x'] + rect['width'] // 2
        center_y = rect['y'] + rect['height'] // 2
        offset = int(30 * intensity)

        action = TouchAction(self.driver)
        action.press(x=center_x, y=center_y)\
            .wait(100)\
            .move_to(x=center_x + offset, y=center_y)\
            .wait(50)\
            .move_to(x=center_x - offset, y=center_y)\
            .wait(50)\
            .move_to(x=center_x + offset, y=center_y)\
            .wait(50)\
            .move_to(x=center_x - offset, y=center_y)\
            .wait(50)\
            .move_to(x=center_x, y=center_y)\
            .release()\
            .perform()

    def wait_for_animation(self, timeout: int = 1000):
        """
        Wait for animations to complete
        :param timeout: Maximum time to wait in milliseconds
        """
        time.sleep(timeout / 1000)

    def get_element_screenshot(self, by: str, value: str) -> bytes:
        """
        Take screenshot of specific element
        :return: Screenshot as bytes
        """
        element = self.find_element(by, value)
        return element.screenshot_as_png

    def wait_for_element_attribute(self, by: str, value: str, attribute: str, expected_value: str, 
                                 timeout: int = 10) -> bool:
        """
        Wait for element attribute to have expected value
        :return: True if attribute matches expected value within timeout
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                lambda x: x.find_element(by, value).get_attribute(attribute) == expected_value
            )
            return True
        except TimeoutException:
            return False

    def get_network_connection(self) -> Dict[str, bool]:
        """
        Get current network connection settings
        :return: Dictionary of connection states
        """
        connection = self.driver.network_connection
        return {
            'airplane_mode': bool(connection & 1),
            'wifi': bool(connection & 2),
            'data': bool(connection & 4)
        }

    def set_network_connection(self, airplane_mode: bool = False, wifi: bool = True, data: bool = True):
        """
        Set network connection settings
        """
        connection = (1 if airplane_mode else 0) | (2 if wifi else 0) | (4 if data else 0)
        self.driver.set_network_connection(connection)

    def execute_mobile_command(self, command: str, params: Dict = None):
        """
        Execute mobile-specific command
        :param command: Command name
        :param params: Command parameters
        """
        return self.driver.execute_script(f'mobile: {command}', params or {}) 