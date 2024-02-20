from ananlyst.data_analysis import DataAnalysis
from pages.eachMainPage import EachMainPage
from utilites.utility import Utility
from pages.homePage import HomePage
from pages.browser import Browser
import pandas as pd

class GooggleScraper(Browser):
    def __init__(self, productName):
        self.productName = productName
    
    def runScraper(self):
        #open Browser
        self.openBrowser(self.url)
        # Get Logging for Debugging
        log = Utility.getLogger(self)
        
        # Get Instances
        homePage = HomePage(self.driver)
        eachMainPage = EachMainPage(self.driver)
        
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
        file_path = f"./results/{self.productName}_Raw.csv".replace(" ", "_")
        df_all_page_details.to_csv(file_path , encoding='utf-8-sig')
        log.info("ALL page's details are saved on file")
        print("ALL page's details are saved on file")
        
        # 전처리 & 감성분석
        print("Please wait! Data is preprocessing...")
        dataAnalysis = DataAnalysis(file_path)
        dataAnalysis.preprocessor()
        log.info("ALL Data Preprocessing is done")
        print("ALL Data Preprocessing is done")
        ### Data PreProcessing
        ### CSV file로 받은 다음 전처리!
        ## pf.drop_duplicates('reviews')를 써주면 중복되는 데이터를 제거할 수 있다.

        #self.driver.quit()
        
googgleScraper = GooggleScraper("baby stroller")
googgleScraper.runScraper()