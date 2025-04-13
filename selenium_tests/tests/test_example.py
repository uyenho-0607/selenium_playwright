def test_google_title(driver):
    # Navigate to Google
    driver.get('https://www.google.com')
    
    # Assert that 'Google' is in the title
    assert 'Google' in driver.title