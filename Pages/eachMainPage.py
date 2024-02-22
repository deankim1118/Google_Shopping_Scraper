import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from .browser import Browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .reviewPage import ReviewPage

class EachMainPage():
    def __init__(self, driver):
        self.driver = driver
    
    ####### Page Locator #######
    pageTitle = (By.XPATH,"//span[@role='heading']")
    pageRating = (By.CLASS_NAME, "uYNZm")
    pageTotalReviews = (By.XPATH, "//div[@class='qIEPib']")
    pageFeatures = (By.XPATH, "//div[@class='qWf3pf']")
    pageSellerAndPrice = (By.XPATH,"//tbody[@id='sh-osd__online-sellers-cont']/tr[@jscontroller='d5bMlb']")
    pageSeller = (By.CSS_SELECTOR,"a.b5ycib")
    #pagePrice = (By.CSS_SELECTOR,"span.g9WBQb") 
    pageTotalPrice = (By.CSS_SELECTOR,"div.drzWO") 
    pageAllReviews = (By.XPATH, "//a[normalize-space()='All reviews']")
    pageFooter = (By.XPATH, "//div[@class='SEsAJd u550Qe']")
    ####### Page Locator #######

    
    ####### Get Locators ########
    def getPageTitle(self):
        page_title =  self.driver.find_element(*EachMainPage.pageTitle).text
        assert page_title is not None, "Can't get page_title Locator"
        return page_title
    def getPageRating(self):
        page_Rating = self.driver.find_element(*EachMainPage.pageRating).text
        assert page_Rating is not None, "Can't get pageRating Locator"
        return page_Rating
    def getPageTotalReviews(self):
        page_total_reviews = self.driver.find_element(*EachMainPage.pageTotalReviews).text.split(" ")[0]
        return page_total_reviews
    def getPageFeatures(self):
        #page_Features = [f.text.strip() for f in self.driver.find_elements(*EachMainPage.pageFeatures)[:7]]
        page_Features = [f.text.strip() for f in self.driver.find_elements(*EachMainPage.pageFeatures)]
        # assert page_Features is not None, "Can't get pageFeatures Locator"
        return page_Features
    def getPageSellers(self):
        allSellerAndPrice = []
        iterateCount = 3
        tableSellersAndPrice = self.driver.find_elements(*EachMainPage.pageSellerAndPrice)
        assert len(tableSellersAndPrice) > 0
        if len(tableSellersAndPrice) == 1:
            iterateCount = 1
        elif len(tableSellersAndPrice) == 2:
            iterateCount = 2
        else:
            iterateCount = 3
        for tr in tableSellersAndPrice[:iterateCount]:
            sellerAndPrice = {"seller": [tr.find_element(*EachMainPage.pageSeller).text],
                            "price": [tr.find_element(*EachMainPage.pageTotalPrice).text],
                            }
            allSellerAndPrice.append(sellerAndPrice)
        return allSellerAndPrice
    def getPageAllReviews(self):
        all_reviews_btn = self.driver.find_element(*EachMainPage.pageAllReviews)
        assert all_reviews_btn.text == "All reviews"
        return all_reviews_btn
    def getPageFooter(self):
        page_footer = self.driver.find_element(*EachMainPage.pageFooter)
        return page_footer
    ###### Get Locators ########
    
    ### DataFrame = [제품이름, 평점, 평점갯수, 특징분석단어, {판매처 Top3, 가격}] 가져오기
    def moveToEachPage(self, urlDataFrame):
        wait = Browser.wait
        df_page_details = []
        # df_page_reviews = []
        pages_num = 0
        browser = Browser()
        reviewPage = ReviewPage(self.driver, wait)
        for page in urlDataFrame:
            pages_num += 2
            #Open Browser with get(url)
            browser.openBrowser(page)
            ## Wait until Footer of webpage is visible
            wait.until(EC.visibility_of(self.getPageFooter()))
            # DataFrame = [제품이름, 평점, 평점갯수, 특징분석단어, {판매처 Top3, 가격}] 가져오기
            page_detail = pd.DataFrame({
                            "title": self.getPageTitle(),
                            "url": page,
                            "totalRating": self.getPageRating(),
                            "totalReviews": self.getPageTotalReviews(),
                            "features": self.getPageFeatures(),
                            })
            page_sellers = pd.DataFrame(self.getPageSellers())
            # Wait until All Reviews Button is clickable
            # wait.until(EC.element_to_be_clickable(self.getPageAllReviews()))
            # self.getPageAllReviews().click()
            
            # df_page_reviews = reviewPage.getReviewContents(More_BTN_Click_Count= moreBtnClickCount)
            # df_page_concat = pd.concat([page_detail, page_sellers, df_page_reviews], axis=1)
            df_page_concat = pd.concat([page_detail, page_sellers], axis=1)
            df_page_details.append(df_page_concat)
            ### URL 이 바뀔 때까지 기다려라
            wait.until(EC.url_changes(page[pages_num]))
        df_page_details = pd.concat(df_page_details)
        return df_page_details
        

"""
     ### 각 URL for문으로 돌리기
     ## get(URL[:]) 
     ## DataFrame = [제품이름, 평점, 평점갯수, 특징분석단어, {판매처 Top3, 가격}] 가져오기
      # 판매처 Top3 가져오기
    ### All reviews.Click() 
    ### More reviews.Click() 몇번 클릭할지 고민해보기
    ### Riview 가져올 때 작성자 꼭 넣기! 나중에 데이터를 추가 할때 작성자가 똑같으면 중복데이터를 방지할 수 있다.
"""