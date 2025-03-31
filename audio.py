import pyautogui
import time
from selenium import webdriver

# Initialize Selenium WebDriver
driver = webdriver.Chrome()
driver.get("https://teams.live.com/meet/939822309388?p=ShzATZ6zxesPc339eJ")  # Replace with your URL

# Wait for the dialog to appear (adjust time as needed)
time.sleep(3)  

# Press Escape to dismiss the dialog (same as clicking Cancel)
pyautogui.press('esc')
uGOf1d
print("Dialog dismissed with Escape key")