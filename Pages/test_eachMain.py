from cgitb import text
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd
from browser import Browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from reviewPage import ReviewPage

test_url = "https://www.google.com/shopping/product/8046350165984023408?hl=en&q=baby+bed&prds=eto:13978725414086279408_0;17975152726480525717_0,pid:14813954418085753660,rsk:PC_4230209202587146377&sa=X&ved=0ahUKEwjM0MD61YuEAxXsLzQIHZcEB88Q9pwGCBI"

browser = Browser()
driver = browser.driver

####### Page Locator #######
pageTitle = (By.XPATH,"//span[@role='heading']")
pageRating = (By.XPATH, "//div[@class='uYNZm']")
pageTotalReviews = (By.XPATH, "//div[@class='qIEPib']")
pageFeatures = (By.XPATH, "//div[@class='qWf3pf']")
pageSellerAndPrice = (By.XPATH,"//tbody[@id='sh-osd__online-sellers-cont']/tr[@jscontroller='d5bMlb']")
pageSeller = (By.CSS_SELECTOR,"a.b5ycib") 
# pageItemPrice = (By.CSS_SELECTOR,"span.g9WBQb") div.drzWO
pageTotalPrice = (By.CSS_SELECTOR,"div.drzWO")
pageAllReviews = (By.XPATH, "//a[normalize-space()='All reviews']")
moreReviewsBtn = (By.XPATH, "//div[@id='sh-fp__pagination-button-wrapper']/button")
pageFooter = (By.XPATH, "//div[@class='SEsAJd u550Qe']")
####### Page Locator #######

####### Get Locators ########
def getPageTitle():
    return driver.find_element(*pageTitle).text
def getPageRating():
    return driver.find_element(*pageRating).text
def getPageTotalReviews():
    return driver.find_element(*pageTotalReviews).text.split(" ")[0]
def getPageFeatures():
    return [f.text.strip() for f in driver.find_elements(*pageFeatures)[:5]]
def getPageSellers(iterateCount = 3):
    allSellerAndPrice = []
    iterateCount = iterateCount
    tableSellersAndPrice = driver.find_elements(*pageSellerAndPrice)
    assert len(tableSellersAndPrice) > 0
    if len(tableSellersAndPrice) == 1:
        iterateCount = 1
    elif len(tableSellersAndPrice) == 2:
        iterateCount = 2
    else:
        iterateCount = 3
    for tr in driver.find_elements(*pageSellerAndPrice)[:iterateCount]:
        sellerAndPrice = {"seller": [tr.find_element(*pageSeller).text],
                          "price": [tr.find_element(*pageTotalPrice).text]
                          }
        allSellerAndPrice.append(sellerAndPrice)
    return allSellerAndPrice
def getPageAllReviews():
    all_reviews_btn = driver.find_element(*pageAllReviews)
    assert all_reviews_btn.text == "All reviews"
    return all_reviews_btn
def getMoreReviewsBtn():
    try:
        more_reviews_btn = driver.find_element(*moreReviewsBtn)
        assert more_reviews_btn.text == "More reviews"
        return more_reviews_btn
    except NoSuchElementException:
        pass
  
def getPageFooter():
    page_footer = driver.find_element(*pageFooter)
    return page_footer
# DataFrame = [제품이름, 평점, 평점갯수, 특징분석단어, {판매처 Top3, 가격}] 가져오기


def test():
    df_page_details = []
    df_page_reviews = []
    wait = WebDriverWait(driver, 5)
    reviewPage = ReviewPage(driver, wait)
    pages_num = 0
   
    for page in range(1):
        pages_num += 1
        browser.openBrowser(test_url)
        ## Wait until Footer of webpage is visible
        wait.until(EC.visibility_of(getPageFooter()))
        page_detail = pd.DataFrame({
                        "title": getPageTitle(),
                        "rating": getPageRating(),
                        "totalReview": getPageTotalReviews(),
                        "features": getPageFeatures(),                       
                        })
        page_sellers = pd.DataFrame(getPageSellers())
                                     
        ## Wait until All Reviews Button is clickable and Click
        all_reviews_button = wait.until(EC.element_to_be_clickable(getPageAllReviews()))
        all_reviews_button.click()
    
        ### Wait until More Reviews Button is clickable and Click
        df_page_reviews = reviewPage.getReviewContents()
        df_page_concat = pd.concat([page_detail,page_sellers,df_page_reviews], axis=1)
        df_page_details.append(df_page_concat)
    print(f"Total reveiws are {len(df_page_reviews)}")
        ### Get All the reviews
        #wait.until(EC.url_changes(page[pages_num]))
    df_page_details = pd.concat(df_page_details)
    return df_page_details
    

    
    
        
# def selectReviewContent(review):
#     try: 
#         content = review.find_element(By.CSS_SELECTOR, "div[id*='short']")
#         return content.text
#     except NoSuchElementException:
#         print("Can't fin id='short'")
#         pass
#     try:
#         content = review.find_element(By.CSS_SELECTOR, "div[id*='full']")
#         return content.text
#     except NoSuchElementException:
#         print("Can't fin id='full'")
#         pass
    
print(test())