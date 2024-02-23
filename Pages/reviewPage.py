from cgitb import text
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC

class ReviewPage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        
    ####### Page Locator #######
    moreReviewsBtn = (By.XPATH, "//div[@id='sh-fp__pagination-button-wrapper']/button")
    pageFooter = (By.XPATH, "//div[@class='SEsAJd u550Qe']")
    reviewTables = (By.CSS_SELECTOR, "div.fade-in-animate")
    reviewRating = (By.CSS_SELECTOR, "div > div[role='img']")
    reviewContent = (By.CSS_SELECTOR, "div:nth-child(4)")
    productName = (By.CSS_SELECTOR, "a.BvQan.sh-t__title.sh-t__title-pdp.translate-content")
    ####### Page Locator #######

    ####### Get Locators ########
    # def getMoreReviewsBtn(self):
    #     try:
    #         more_reviews_btn = self.driver.find_element(*self.moreReviewsBtn)
    #         # assert more_reviews_btn.text == "More reviews"
    #         return more_reviews_btn
    #     except NoSuchElementException:
    #         pass
    def getMoreReviewsBtn(self):
        more_reviews_btn = self.driver.find_element(*self.moreReviewsBtn)
        #assert more_reviews_btn.text == "More reviews"
        return more_reviews_btn
    
    def getPageFooter(self):
        page_footer = self.driver.find_element(*self.pageFooter)
        return page_footer

    def getReviewTables(self, ):
        review_tables = self.driver.find_elements(*self.reviewTables)
        return review_tables
    def getReviewRating(self, element):
        # review_rating = element.find_element(*self.reviewRating).get_attribute("aria-label").split("out of")[0].strip() + " stars"
        ## 평점 Data 분석을 위해 int로 바꿈
        review_rating = element.find_element(*self.reviewRating).get_attribute("aria-label").split("out of")[0].strip()
        return str(review_rating)
    def getReviewContent(self, element):
        review_content = element.find_element(*self.reviewContent).text
        return review_content
    def getProductName(self):
        product_name = self.driver.find_element(*self.productName).text
        return product_name
    ####### Get Locators ########

    ######## Scroll & Click ########      
    def waitAndClickMore(self, wait, btnClickCount):
        for count in range(btnClickCount):
            #driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
            ActionChains(self.driver).scroll_to_element(self.getMoreReviewsBtn()).perform()
            wait.until(EC.visibility_of_element_located(self.moreReviewsBtn))
            # wait.until(EC.element_to_be_clickable(self.getMoreReviewsBtn()))
            # time.sleep(0.5)
            ActionChains(self.driver).scroll_to_element(self.getPageFooter()).perform()
            wait.until(EC.visibility_of_element_located(self.pageFooter))
            self.getMoreReviewsBtn().click()
            time.sleep(0.4)
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='sh-fp__pagination-button-wrapper']/button/div[@class='_-ik']")))
            wait.until(EC.presence_of_element_located(self.moreReviewsBtn))
            # wait.until(EC.text_to_be_present_in_element(self.moreReviewsBtn,'More reviews'))
           
    def scrollTo(self):
        ActionChains(self.driver).scroll_to_element(self.getPageFooter()).perform()
    ######## Get Reviews and Ratings ########
    # More_BTN_Click_Count = 23
    def getReviewContents(self, More_BTN_Click_Count):
        print(More_BTN_Click_Count)
        df_page_reviews = []
        product = self.getProductName()
        # Scroll and Click More Button
        # self.waitAndClickMore(self.wait, btnClickCount = self.More_BTN_Click_Count)
        self.waitAndClickMore(self.wait, btnClickCount = More_BTN_Click_Count)
        # Get review ratings and contents in the MoreReviews Page
        self.scrollTo()
        for review in self.driver.find_elements(By.CSS_SELECTOR, "div.fade-in-animate"):
            all_reviews = {
                            "product" : product,
                            "rating" : self.getReviewRating(review),
                            "reviews" : self.getReviewContent(review)
                        }
            df_page_reviews.append(all_reviews)
                
        print(f"Total reveiws are {len(df_page_reviews)}")
        df_page_reviews = pd.DataFrame(df_page_reviews) 
        
        return df_page_reviews
    
    
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


