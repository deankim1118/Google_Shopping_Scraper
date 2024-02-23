from pages.browser import Browser
from pages.eachMainPage import EachMainPage
from utilites.utility import Utility
from pages.homePage import HomePage
from ananlyst.data_analysis import DataAnalysis
import pandas as pd

class GooggleScraper(Browser):
    def __init__(self, productName):
        self.productName = productName
    
    def runScraper(self):
        #open Browser
        self.openBrowser(self.url)
        
        # Get Instances
        homePage = HomePage(self.driver)
        eachMainPage = EachMainPage(self.driver)
        utility = Utility()
        
        # Get Logging for Debugging
        log = utility.getLogger()
        
        # Search Products on Google  
        homePage.searchProduct(self.productName)
        log.info(f"{self.productName} is searched on Google")
        print(f"{self.productName} is searching on Google...")
        
        # Enter rating 4 an up
        homePage.clickRating4Up()
        log.info("Toggled rating 4 and up")
        print("Toggled rating 4 and up")
        
        # Sponsered 제외한 모든 제품 [Products details URL, 평점갯수] 가져오기
        print("Please wait! I'm getting all product's URLs...")
        list_all_products = homePage.intoListAllProducts()
        log.info("Got all product's URLs")
        print("Got all product's URLs")
        
        # get URL List in Pandas DataFrame 평점갯수 > 200 필터링
        print(f"Please Wait! {self.productName} are filtering")
        df_all_product_urls = homePage.intoDataFrame(allProducts=list_all_products, ratingFilterNum=290)
        log.info(f"{len(df_all_product_urls)} of {self.productName} are filtered out")
        print(f"{len(df_all_product_urls)} of {self.productName} are filtered out")
        
        # Move to each Page
        print("Please wait! I'm scraping all products...")
        df_all_page_details = eachMainPage.moveToEachPage(urlDataFrame=df_all_product_urls)
        log.info("All page is loaded")
        print(f"Congrates! All {self.productName}'s scraping is done!!!")
        
        # Save to Excel file
        file_path_Raw = f"./results/{self.productName}_Raw.csv".replace(" ", "_")
        df_all_page_details.to_csv(file_path_Raw , encoding='utf-8-sig')
        log.info("ALL page's details are saved on file")
        print("ALL page's details are saved on file")
        
        # Scrap & Raw 에서 features 전처리 & Save as df_V2.csv return V2 dataFrame
        print("Please wait! Data is preprocessing...")
        dataAnalysis = DataAnalysis(file_path_Raw)
        df_V2 = dataAnalysis.preprocessor()
        log.info("Split Features Column to new columns and save as df_V2.CSV!")
        log.info("ALL Data Preprocessing is done")
        print("Split Features Column to new columns and save as df_V2.CSV!")
        print("ALL Data Preprocessing is done")
        
        ### 1. V2 데이터프레임에서 (totalRating,totalReviews,PosNegMainFeatures,percentOfMainFeatures)로 Best 10 뽑기
        log.info("Pick Best 10 Products in First Stage...")
        print("Pick Best 10 Products in First Stage...")
        best_ten_products = dataAnalysis.bestTenFirst(self.df_v2)
        log.info("We Pick All Best 10 Products!")
        print("We Pick All Best 10 Products!")
        ### 2. Get Url + moveToEachReviewPage 
        ### 2. Scraping Best10 Reviews & ratings, moreBtnClickCount =  average_reviews / 10, maximum 350 리뷰 이하로 Scrap
        ## 2-1. Get Best 10 url and average reviews
        urls_best_ten, average_reviews = best_ten_products['url'], best_ten_products['average_reviews']
        ## 2-2. Scrap Best10 and moreBtnClickCount = Review 합계에 따라서 다르게 하기! Max 29! Total Reviews / 10 - 2
        log.info("Please wait! I'm scraping Best 10 all Reviews...")
        print("Please wait! I'm scraping Best 10 all Reviews...")
        eachMainPage.moveToEachReviewPage(urls_best_ten, moreBtnClickCount = utility.getMoreBtnNumber(df=best_ten_products, urls_best_ten=urls_best_ten))
        log.info(f"Congrates! All {self.productName}'s Best 10's scraping is done!!!")
        print(f"Congrates! All {self.productName}'s Best 10's scraping is done!!!")
        #self.driver.quit()
        
googgleScraper = GooggleScraper("baby bed")
googgleScraper.runScraper()