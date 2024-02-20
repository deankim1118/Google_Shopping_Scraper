from cgitb import text
import time
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import pandas as pd
from browser import Browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reviewPage import ReviewPage

test_url = "https://www.google.com/shopping/product/14866794585966689624?hl=en&q=baby+bed&prds=eto:9954537065424387205_0;16973966374304431477_0;7341088065666325988_0,pid:17748213720284870968,rsk:PC_7291201009253003074&sa=X&ved=0ahUKEwi18OLXpYuEAxX1MlkFHf4WDUIQ9pwGCBY"

browser = Browser()
driver = browser.driver

productName = (By.XPATH, "//span[@role='heading']")
browser.openBrowser(test_url)
def getProductName():
    product_name = driver.find_element(*productName).text
    return product_name

print(getProductName())