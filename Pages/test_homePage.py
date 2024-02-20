import pandas as pd
from selenium.webdriver.common.by import By

from pages.browser import Browser

test_url = "https://www.google.com/search?sca_esv=ab1ad2f69166e203&hl=en&tbm=shop&sxsrf=ACQVn0_BGWwfCe7k7O31EC0j2ZhMQonVnw:1706829817441&psb=1&q=baby+bed&tbs=mr:1,avg_rating:400&sa=X&ved=0ahUKEwiS8dbHpIuEAxWBF1kFHcikBycQz90GCI4PKAA&biw=1440&bih=1443&dpr=1.5"

browser = Browser()
driver = browser.driver

    
####### Page Locator #######
all_products = (By.CSS_SELECTOR, "a.Lq5OHe[href*='shopping/product']")
####### Page Locator #######

####### Get Locators ########

def getAllProducts():
    allProducts = driver.find_elements(all_products)
    assert allProducts is not None, "Can't get All Products Locator"
    return allProducts
####### Get Locators ########

### Sponsered 제외한 모든 제품 [Products details URL, 평점갯수] 가져오기  
def intoListAllProducts():
    list_all_products = []
    # Get all products Locator
    all_products = getAllProducts()
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
def intoDataFrame(allProducts, ratingFilterNum):
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
href="/shopping/product/7764820066358109651?sca_esv=ab1ad2f69166e203&hl=en&sxsrf=ACQVn0_BGWwfCe7k7O31EC0j2ZhMQonVnw:1706829817441&psb=1&q=baby+bed&biw=1440&bih=1443&dpr=1.5&prds=eto:1542379202798317840_0,pid:1789757211587714337,rsk:PC_2227663781939114518&sa=X&ved=0ahUKEwicqYzi9IuEAxU-D1kFHa71DIoQ8wIItBI"

### 각 URL for문으로 돌리기
    ## get(URL[:]) 
    ## DataFrame = [제품이름, 평점, 평점갯수, 특징분석단어, {판매처 Top3, 가격}] 가져오기
    # 판매처 Top3 가져오기
### All reviews.Click() 
### More reviews.Click() 몇번 클릭할지 고민해보기
### Riview 가져올 때 작성자 꼭 넣기! 나중에 데이터를 추가 할때 작성자가 똑같으면 중복데이터를 방지할 수 있다.
"""

    