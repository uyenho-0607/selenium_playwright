import pytest
from playwright.sync_api import Page

@pytest.fixture(scope='function')
def context_config(playwright_browser_context_args):
    """Update browser context configuration if needed"""
    playwright_browser_context_args.update({
        'viewport': {'width': 1920, 'height': 1080}
    })
    return playwright_browser_context_args