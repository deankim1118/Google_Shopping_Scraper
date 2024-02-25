from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait

class Browser: 
    url = "https://shopping.google.com/"
        
    test_url = "https://www.google.com/search?sca_esv=de7a49ba27450786&hl=en&tbm=shop&sxsrf=ACQVn0_IJda3GGKIGfNSClaAoLnwc8sd2w:1706716904577&psb=1&q=bicycle&tbs=mr:1,avg_rating:400&sa=X&ved=0ahUKEwjnvtD2_4eEAxUCFVkFHSZ9DO8Qz90GCIERKAA&biw=1440&bih=2391&dpr=1.5#spd=0"

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    # options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    ##Chrome Driver
    service_obj = Service("C:/Users/deank/OneDrive/Investments/Best_Reviews__Blog/Scraper/chromedriver-win64/chromedriver-win64/chromedriver.exe")
    
    driver = webdriver.Chrome(options=options, service=service_obj) 
    wait = WebDriverWait(driver, 10)
    def openBrowser(self, url):
        try:
            Browser.driver.get(url)
            # Browser.driver.maximize_window()
            Browser.driver.implicitly_wait(5)
        except Exception as err:
            print(type(err))

    
