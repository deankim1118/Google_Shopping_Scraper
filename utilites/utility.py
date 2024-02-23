import inspect
import logging
from pages.browser import Browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select


class Utility:
    driver = Browser.driver
    
    def verifyLinkPresence(self, text):
        element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, text)))
        
    def selectOptionByText(self, locator, text):
        sel = Select(locator)
        sel.select_by_visible_text(text)
        
    def getLogger(self):
        loggerName = inspect.stack()[1][3]
        logger = logging.getLogger(loggerName)
        fileHandler = logging.FileHandler('logfile.log')
        formatter = logging.Formatter("%(asctime)s :%(levelname)s : %(name)s :%(message)s")
        fileHandler.setFormatter(formatter)

        logger.addHandler(fileHandler)  # filehandler object

        logger.setLevel(logging.DEBUG)
        return logger
    
    # Review 합계에 따라서 다르게 하기! Max 29! Total Reviews / 10 - 2
    def getMoreBtnNumber(self, df, urls_best_ten):
        # baby_bed_bestTen DataFrame에서 해당 URL이 있는 행 찾기
        matching_row = df[df['url'] == urls_best_ten]

        # 해당 행이 존재하면 average_reviews 값 추출 및 함수 호출
        if not matching_row.empty:
            average_reviews = matching_row.iloc[0]['average_reviews']
            if average_reviews >= 330:
                moreBtnClickCount = 29
            else:
                moreBtnClickCount = int(average_reviews / 10 - 3)
        return moreBtnClickCount