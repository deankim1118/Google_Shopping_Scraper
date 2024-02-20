import pandas as pd
from selenium.webdriver.common.by import By

class HomePage:
    def __init__(self, driver):
        self.driver = driver
        
    ####### Page Locator #######
    googleSearchInput = (By.NAME, "q")
    searchEnter = (By.XPATH, "//*[@id='kO001e']/div/div/c-wiz/form/div[2]/div[1]/button/div")
    rating4Up = (By.CLASS_NAME, 'cNaB2e')
    all_products = (By.CSS_SELECTOR, "a.Lq5OHe[href*='shopping/product']")
    # all_products = (By.CSS_SELECTOR, "a[class='Lq5OHe eaGTj translate-content']")
    ####### Page Locator #######
    
    ####### Get Locators ########
    def getGoogleSearchInput(self):
        search_input = self.driver.find_element(*HomePage.googleSearchInput)
        assert search_input is not None, "Can't find GoogleSearchInput Locator"
        return search_input
    def getSearchEnter(self):
        search_Enter = self.driver.find_element(*HomePage.searchEnter)
        assert search_Enter is not None, "Can't find Enter for searchInput Locator"
        return search_Enter
    def getRating4Up(self):
        rating4Up = self.driver.find_elements(*HomePage.rating4Up)[0]
        assert rating4Up is not None, "Can't find rating4Up toggle button Locator"
        return rating4Up
    def getAllProducts(self):
        allProducts = self.driver.find_elements(*HomePage.all_products)
        assert allProducts is not None, "Can't get All Products Locator"
        return allProducts
    ####### Get Locators ########
    
    ####### Main Tasks ########
    def searchProduct(self, productName):
        ## Google Search product
        self.getGoogleSearchInput().send_keys(productName)
        ## Enter after searching
        self.getSearchEnter().click()
        
    def clickRating4Up(self):
        ## Enter review rating 4 and up
        rating_4 = self.getRating4Up()
        # Error 처리 False 면 Error
        assert "4" in rating_4.text
        rating_4.click()       
    
    ### Sponsered 제외한 모든 제품 [Products details URL, 평점갯수] 가져오기  
    def intoListAllProducts(self):
        list_all_products = []
        # Get all products Locator
        all_products = self.getAllProducts()
        # get URL & Rating number
        for product in all_products:
            # get rating for all products Locator 
            rating_texts = product.find_element(By.TAG_NAME,"span")
            # into dict
            product = { 
                       "url": product.get_attribute("href"), 
                       "rating": rating_texts.text[3:].strip(),
                       }
            # into List
            list_all_products.append(product)
        return list_all_products
    ### Pandas DataFrame에 넣고 평점갯수 > 200 필터링
    def intoDataFrame(self, allProducts, ratingFilterNum):
        ## Pandas DataFrame
        df_all_products = pd.DataFrame(allProducts)
        ## Filter rating > 200
        # 1,000 Comma 제거하고 String to Float
        df_all_products["rating"] = df_all_products["rating"].str.replace(",","", regex=True).apply(pd.to_numeric)
        # Filter rating > 200
        rating_condition = df_all_products["rating"] > ratingFilterNum
        df_all_products = df_all_products.loc[rating_condition].reset_index(drop=True)
        # Filter only URL values
        df_all_products = df_all_products["url"].values
        return df_all_products
                    
    """
    
    ### 각 URL for문으로 돌리기
     ## get(URL[:]) 
     ## DataFrame = [제품이름, 평점, 평점갯수, 특징분석단어, {판매처 Top3, 가격}] 가져오기
      # 판매처 Top3 가져오기
    ### All reviews.Click() 
    ### More reviews.Click() 몇번 클릭할지 고민해보기
    ### Riview 가져올 때 작성자 꼭 넣기! 나중에 데이터를 추가 할때 작성자가 똑같으면 중복데이터를 방지할 수 있다.
    """
    
        