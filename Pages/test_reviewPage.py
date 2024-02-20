from cgitb import text
import time
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import pandas as pd
from browser import Browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from textblob import TextBlob

test_url = ["https://www.google.com/shopping/product/5198109520084688256/reviews?hl=en&q=baby+socks&prds=eto:11332302076298538762_0;9679370530065262880_0,local:1,pid:1101633888456910326,prmr:2,rsk:PC_6420868670458799872&sa=X&ved=0ahUKEwi_1rqSh66EAxX9EFkFHXqVCQMQqSQITQ"]

browser = Browser()
driver = browser.driver

#browser.openBrowser("https://www.google.com/shopping/")
####### Page Locator #######
moreReviewsBtn = (By.XPATH, "//div[@id='sh-fp__pagination-button-wrapper']/button")
pageFooter = (By.XPATH, "//div[@class='SEsAJd u550Qe']")
reviewTables = (By.CSS_SELECTOR, "div.fade-in-animate")
reviewRating = (By.CSS_SELECTOR, "div > div[role='img']")
reviewContent = (By.CSS_SELECTOR, "div:nth-child(4)")
productName = (By.CSS_SELECTOR, "a.BvQan.sh-t__title.sh-t__title-pdp.translate-content")
####### Page Locator #######

####### Get Locators ########
def getMoreReviewsBtn():
    try:
        more_reviews_btn = driver.find_element(*moreReviewsBtn)
        # assert more_reviews_btn.text == "More reviews"
        return more_reviews_btn
    except NoSuchElementException:
        pass
def getPageFooter():
    page_footer = driver.find_element(*pageFooter)
    return page_footer

def getReviewTables():
    review_tables = driver.find_elements(*reviewTables)
    return review_tables
def getReviewRating(element):
    review_rating = element.find_element(*reviewRating).get_attribute("aria-label").split("out of")[0].strip() + " stars"
    return str(review_rating)
def getReviewContent(element):
    review_content = element.find_element(*reviewContent).text
    return review_content
def getProductName():
    product_name = driver.find_element(*productName).text
    return product_name
####### Get Locators ########

def test():
    df_page_reviews = []
    wait = WebDriverWait(driver, 10)
    browser.openBrowser(test_url[0])
    product = getProductName()

    waitAndClickMore(wait, clickCount= 20)
        # Get review ratings and contents in the MoreReviews Page
    
    for review in getReviewTables():
        all_reviews = {
                        "product" : product,
                        "rating" : getReviewRating(review),
                        "reviews" : getReviewContent(review)
                    }
        df_page_reviews.append(all_reviews)
    df_page_reviews = pd.DataFrame(df_page_reviews) 
    all_reviews_result = df_page_reviews["reviews"]
    print(f"Total reveiws are {len(df_page_reviews)}")
        ### Get All the reviews
        #wait.until(EC.url_changes(page[pages_num]))
    # df_page_details = pd.concat(df_page_details)
    return all_reviews_result

# def waitAndClickMore(wait, clickCount):
#     for count in range(clickCount):
#         ActionChains(driver).scroll_to_element(getPageFooter()).perform()
#         wait.until(EC.visibility_of(getPageFooter()))
#         getMoreReviewsBtn().click()
#         time.sleep(0.8)
        
def waitAndClickMore(wait, clickCount):
    for count in range(clickCount):
        #driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
        ActionChains(driver).scroll_to_element(getPageFooter()).perform()
        wait.until(EC.visibility_of_element_located(moreReviewsBtn))
        ActionChains(driver).scroll_to_element(getPageFooter()).perform()
        wait.until(EC.visibility_of_element_located(pageFooter))
        getMoreReviewsBtn().click()
        time.sleep(0.4)
        # wait.until(EC.presence_of_element_located(moreReviewsBtn))
        wait.until(EC.text_to_be_present_in_element((By.XPATH, "//div[@id='sh-fp__pagination-button-wrapper']/button"), 'More reviews'))
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='sh-fp__pagination-button-wrapper']/button/div[@class='_-ik']")))
        
print(test())
### 감성분석 TEST
# all_review_data = test()
# results = { "Positive" : 0, "Negative" : 0, "Neutral" : 0}
# for t in all_review_data:
#     analyst = TextBlob(t)
    
#     pos_neg = analyst.sentiment.polarity
#     if pos_neg == 0:
#         results["Neutral"] += 1
#     elif pos_neg > 0:
#         results["Positive"] += 1
#     elif pos_neg < 0:
#         results["Negative"] += 1
# posPercent = results["Positive"] / (results["Positive"] + results["Negative"]) * 100 
# negPercent = 100 - posPercent
# print(results, f"Positive:{posPercent}%, Negative:{negPercent}%")

