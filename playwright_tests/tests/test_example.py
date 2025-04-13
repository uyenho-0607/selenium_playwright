from playwright.sync_api import Page, expect

def test_google_title(page: Page):
    # Navigate to Google
    page.goto('https://www.google.com')
    
    # Assert that 'Google' is in the title
    expect(page).to_have_title("Google")