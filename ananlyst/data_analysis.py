from collections import defaultdict
import re
import numpy as np
import pandas as pd
from textblob import TextBlob


class DataAnalysis:
    def __init__(self, filePath) -> None:
        self.filePath = filePath
        # self.filePath = "./results/baby_double_strollers_Raw.csv"
    
    def preprocessor(self):      
        """ 0. Review 제외하고 Scrap & Raw 에서 features 전처리. 
                EachMainPage.moveToEachPage(df)
                DataAnalysis.splitMainFeatures(df_raw)
            1. v2.csv에서 (totalRating,totalReviews,PosNegMainFeatures,finalFeatureScore)로 Best 10 뽑기
                DataAnalysis.bestTenFirst(df_v2)
            2. Scraping Best10 Reviews & ratings, moreBtnClickCount =  average_reviews / 10, maximum 300 리뷰 이하로 Scrap
            3. Best10 Sentiment Analysis 
            4. Best10의 main_features Score
            5. Best5 뽑기
            6. Best5의 main_feature, featureScore, percentOfMainFeatures 가져오기 bestFive()실행 후
        """

        df_raw = pd.read_csv(self.filePath).drop_duplicates(subset=['title', 'features']).reset_index(drop=True)
        # df_review = df_raw[['title','url','seller','price','totalRating','totalReviews','features']]
        ### Save as xlsx Excel file
        df_raw_xlsx = self.replaceCsvToXlsx()
        df_raw.to_excel(df_raw_xlsx ,sheet_name='Raw', index=False, engine='openpyxl')
          
        ### 0. Scrap & Raw 에서 features 전처리.
        df_v2 = self.splitMainFeatures(df_raw)
        ### 0-1. finalFeatureScore < 4.9 이하 지우기
        df_v2 = df_v2[df_v2['finalFeatureScore'] > 4.9].dropna(subset='finalFeatureScore').reset_index(drop=True)
        ## 0-1.Save as csv
        # df_v2.to_csv(f'{self.filePath.replace('Raw', 'V2')}', encoding='utf-8-sig')
        ## 0-2. V2데이터를 전처리 후에 Product_All.xlsc 의 새로운 Sheet에 저장.
        ## 0-2. Excel writer를 사용하여 Excel 파일로 저장합니다.
        self.addToExcelSheet(dataFrame = df_v2, sheetName='V2')
        
        return df_v2
    
    def replaceCsvToXlsx(self):
        ### Save as xlsx
        df_raw_xlsx = self.filePath.replace('Raw.csv', 'All.xlsx')
        return df_raw_xlsx
    
    def addToExcelSheet(self, dataFrame, sheetName):
        df_raw_xlsx = self.replaceCsvToXlsx()
        # Excel writer를 사용하여 Excel 파일로 저장합니다.
        with pd.ExcelWriter(df_raw_xlsx, engine='openpyxl', mode='a') as writer:
            # 전처리된 데이터를 'V2' 시트에 저장합니다.
            dataFrame.to_excel(writer, sheet_name=sheetName, index=False)
        
     ### Sentiment Analysis
    def sentimentAnalysis(self, df):
        sentimentAnalysis = []
        for text in df['reviews']:
            analyst = TextBlob(text)
            pos_neg = analyst.sentiment.polarity
            
            # sentimentAnalysis.append(pos_neg)
            if pos_neg == 0:
                sentimentAnalysis.append(0)
            elif pos_neg > 0:
                sentimentAnalysis.append(1)
            elif pos_neg < 0:
                sentimentAnalysis.append(-1)
            else:
                sentimentAnalysis.append('NAN')       
                
        df_copy = df.copy()
        df_copy['sentimentAnalysis'] = sentimentAnalysis
        df_sentiment = df_copy.query("sentimentAnalysis != 0")
        self.addToExcelSheet(df_sentiment, 'sentiment')

        return df_sentiment
        
    def splitMainFeatures(self, df):
        split_features = df['features'].str.split('(', expand= True)
        df['main_features'] = split_features[0]
        num_of_mainFeatures = split_features[1].str.split(')', expand=True)[0].apply(pd.to_numeric, errors='coerce')
        df['totalReviews'] = df['totalReviews'].replace(',', '', regex=True).apply(pd.to_numeric, errors='coerce')
        df['numOfMainFeatures'] = num_of_mainFeatures
        df['finalFeatureScore'] = (num_of_mainFeatures / df['totalReviews'] * 100).round(1)
        pos_neg_mainFeatures = df['features'].str.split('.', expand=True)[1]
        df['PosNegMainFeatures'] = pos_neg_mainFeatures
        # pos_neg_mainFeatures = df['features'].str.split('.', expand=True)[1].str.split('%', expand=True)
        # df['percentPosNeg'] = pos_neg_mainFeatures[0]
        # df['PosNegMainFeatures'] = pos_neg_mainFeatures[1]
        return df
        
    def groupMainFeatures(self, df):
        # group_mainFeatures = df.groupby(['main_features','product','PosNegMainFeatures'])['finalFeatureScore'].mean()
        # group_mainFeatures.to_csv(f'{self.filePath.replace('Raw', 'MainFeatures')}', encoding='utf-8-sig')
        group_mainFeatures = df.groupby(['main_features','title','PosNegMainFeatures','totalRating','totalReviews','numOfMainFeatures'])['finalFeatureScore'].mean()
        group_mainFeatures.to_csv(f'{self.filePath.replace('Raw', 'MainFeatures')}', encoding='utf-8-sig')
        return group_mainFeatures
    
    def bestTenFirst(self, df):
        # PosNegMainFeatures에서 긍정 리뷰의 비율을 숫자로 변환
        df_score = df.copy()
        df_score['positive_review_percentage'] = df_score['PosNegMainFeatures'].apply(lambda x: float(x.split('%')[0]) if "positive" in x else None)
        df_score = df_score.dropna(subset=['positive_review_percentage']).reset_index(drop=True)
       
        # 각 제품별로 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 계산
        product_analysis = df_score.groupby(['title', 'url']).agg(
            average_total_rating=('totalRating', 'mean'),
            average_reviews=('totalReviews', 'mean'),
            sum_positive_percentOfMainFeatures=('percentOfMainFeatures', 'sum'),
            positive_positive_review_percentage=('positive_review_percentage', 'mean'),
        ).reset_index()
        ### 'main_features','final_score','PosNegMainFeatures'
        # 리뷰 수의 로그 변환 적용
        product_analysis['log_reviews'] = np.log1p(product_analysis['average_reviews']) # 총 리뷰수
        # 로그 변환된 리뷰 수를 정규화할 필요가 없으므로, 직접 종합 점수 계산에 포함
        product_analysis['final_score'] = (
            product_analysis['average_total_rating'] / 5 * 1.0 +  # 총 평점! 5점 만점으로 정규화된 점수 
            product_analysis['sum_positive_percentOfMainFeatures'] / product_analysis['sum_positive_percentOfMainFeatures'].max() * 1.5 +  # 긍정 키워드 비율 5점 만점으로 정규화된 점수
            product_analysis['positive_positive_review_percentage'] / 100 * 1.0 +  # 긍정 키워드 감성분석 비율 5점 만점으로 정규화된 점수
            product_analysis['log_reviews'] / product_analysis['log_reviews'].max() * 1.5  # 최대 로그 리뷰 점수로 정규화
        ) #* 10 / (2.0 + 3.0 + 2.0 + 3.0)
        
         # data['score'] = data.apply(lambda x: ((x['finalFeatureScore'] / 100) * 2.5 + (x['positive_review_percentage'] / 100) * 2.5) if pd.notnull(x['positive_review_percentage']) else 0, axis=1)

        # 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 기준으로 상위 5개 제품 선정
        top_10_products = product_analysis.sort_values(by='final_score', ascending=False).head(10).reset_index(drop=True)
        # top_10_products.to_csv(f'{self.filePath.replace('Raw', 'bestTen')}', encoding='utf-8-sig')
        self.addToExcelSheet(dataFrame=top_10_products, sheetName='best11')
  
        return top_10_products
        
    def preprocessorBestTen(self):      
        ## Read Review Excel File
        df_reviews = pd.read_excel("./results/double_strollers_All.xlsx", 'reviews').drop_duplicates(subset=['title', 'reviews']).reset_index(drop=True)
        df_reviews = df_reviews[['product','url','seller','price','totalRating','totalReviews','features','reviews']]
    
        ### 0.  features 전처리.
        df_v3 = self.splitMainFeatures(df_reviews)
        ### 0-1. finalFeatureScore < 4.9 이하 지우기
        
        ## 0-2. V2데이터를 전처리 후에 Product_All.xlsc 의 새로운 Sheet에 저장.
        ## 0-2. Excel writer를 사용하여 Excel 파일로 저장합니다.
        # self.addToExcelSheet(dataFrame = df_v3, sheetName='V3')
        df_sentiment = self.sentimentAnalysis(df_v3)
        
        return df_sentiment
    # def bestTenProducts(self, df):
    #     # 'positive_sentiment' 컬럼 추가: 1은 긍정, -1은 부정
    #     df['positive_sentiment'] = df['sentimentAnalysis'].apply(lambda x: 1 if x == 1 else 0)

    #     # 각 제품별로 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 계산
    #     product_analysis = df.groupby(['product','url']).agg(
    #         average_total_rating=('totalRating', 'mean'),
    #         average_reviews=('totalReviews', 'mean'),
    #         average_rating=('rating', 'mean'),
    #         positive_sentiment_rate=('positive_sentiment', 'mean')
    #     ).reset_index()
        
    #     # 리뷰 수의 로그 변환 적용
    #     product_analysis['log_reviews'] = np.log1p(product_analysis['average_reviews'])
    #     # 로그 변환된 리뷰 수를 정규화할 필요가 없으므로, 직접 종합 점수 계산에 포함
    #     product_analysis['normalized_sentiment'] = product_analysis['positive_sentiment_rate'] * 5
    #     product_analysis['finalFeatureScore'] = (
    #         product_analysis['average_total_rating'] / 5 * 2.0 +  # 5점 만점으로 정규화된 점수
    #         product_analysis['average_rating'] / 5 * 2.0 +  # 5점 만점으로 정규화된 점수
    #         product_analysis['normalized_sentiment'] / 5 * 3.0 +  # 5점 만점으로 정규화된 점수
    #         product_analysis['log_reviews'] / product_analysis['log_reviews'].max() * 3.0  # 최대 로그 리뷰 점수로 정규화
    #     ) * 10 / (2.0 + 2.0 + 3.0 + 3.0) 
    #     # 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 기준으로 상위 10개 제품 선정
    #     top_10_products_log = product_analysis.sort_values(by='finalFeatureScore', ascending=False).head(10)
    #     # Save to file
    #     top_10_products_log.to_csv(f'{self.filePath.replace('Raw', 'bestTen')}', encoding='utf-8-sig')
        
    # "PosNegMainFeatures" 컬럼에서 긍정,부정 비율 추출 함수
    def extract_percentage(self, column, patternString):
        # 입력 값이 문자열이 아닌 경우 None 반환
        if not isinstance(column, str):
            return None
        match = re.search(patternString, column)
        if match:
            return int(match.group(1))
        else:
            return None   
    # 각 제품별 주요 기능의 긍정 비율, 평균 평점, 그리고 주요 기능 비율을 기반으로 종합 점수 계산
    def calScore(self, df, percentEachFeature=4.5):
        # "PosNegMainFeatures" 컬럼에서 긍정 및 부정 비율을 추출하고 저장
        df['PositivePercentage'] = df['PosNegMainFeatures'].apply(lambda x: self.extract_percentage(x, r'(\d+)% of the reviews are positive'))
        df['NegativePercentage'] = df['PosNegMainFeatures'].apply(lambda x: self.extract_percentage(x, r'(\d+)% of the reviews are negative'))
        
        # 제품별 main_features와 PositivePercentage를 기반으로 점수 계산
        product_feature_scores = defaultdict(dict)

        # 각 제품 및 주요 기능별로 PositivePercentage 평균 계산
        for product in df['product'].unique():
            product_df = df[df['product'] == product]
            features = product_df['main_features'].unique()
            # print(easy_to_use_count)
            for feature in features:
                feature_df = product_df[product_df['main_features'] == feature]
                if not feature_df.empty and feature_df['finalFeatureScore'].item() >= percentEachFeature:
                    row_index = feature_df.index[0]
                    # 평균 긍정 및 부정 비율 계산
                    positive_percentage_avg = feature_df['PositivePercentage'].mean()
                    negative_percentage_avg = feature_df['NegativePercentage'].mean()
                    # 주요 기능 비율 계산
                    percent_of_main_features_avg = feature_df['finalFeatureScore'].sum()
                    # 점수 계산
                    if not pd.isnull(positive_percentage_avg):
                        positive_score = (positive_percentage_avg / 100) * 4.5
                    else:
                        positive_score = None
                    
                    if not pd.isnull(negative_percentage_avg):
                        negative_score = 5 - (negative_percentage_avg / 100) * 3
                    else:
                        negative_score = None
                    
                    # 주요 기능 비율을 기반으로 추가 점수 계산 (최대 1점 추가)
                    additional_score = (percent_of_main_features_avg / df['finalFeatureScore'].max()) * 2
                    # 종합 점수 계산: 기본 점수 + 추가 점수
                    if positive_score != None:
                        finalFeatureScore = positive_score + additional_score
                    elif negative_score != None:
                        finalFeatureScore = negative_score - additional_score
                    # 점수를 5점 만점으로 제한
                    finalFeatureScore = min(finalFeatureScore, 5)
                    # 결과 저장
                    product_feature_scores[product][feature] = {
                        'PositiveScore': positive_score,
                        'NegativeScore': negative_score,
                        'FinalScore': round(finalFeatureScore, 2),
                        'PosNegPercentage' : feature_df['finalFeatureScore'].mean(),
                    }
                    df.loc[row_index, 'finalFeatureScore'] = round(finalFeatureScore, 2)
        self.addToExcelSheet(df, 'finalFeatureScore')
        return df
                    
        # # DataFrame으로 변환
        # results = []
        # for product, features in product_feature_scores.items():
        #     for feature, scores in features.items():
        #         results.append({
        #             'Product': product,
        #             'Feature': feature,
        #             'PositiveScore': scores['PositiveScore'],
        #             'NegativeScore': scores['NegativeScore'],
        #             'FinalScore': scores['FinalScore'],
        #             'PosNegPercentage' : scores['PosNegPercentage'],
        #         })
        # df_score = pd.DataFrame(results)
        # # Add the "Easy to use score" to the DataFrame
        # df_score.to_csv(f'{self.filePath.replace('Raw', 'ScoreByFeature')}', encoding='utf-8-sig')
    
    def bestFive(self, df):
        # PosNegMainFeatures에서 긍정 리뷰의 비율을 숫자로 변환
        df_score = df.copy()
       
        # 각 제품별로 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 계산
        product_analysis = df_score.groupby(['product', 'url']).agg(
            average_total_rating=('totalRating', 'mean'),
            average_reviews=('totalReviews', 'mean'),
            average_feature_score=('finalFeatureScore', 'mean'),
            positive_sentiment_rate=('sentimentAnalysis', 'mean')
        ).reset_index()

        # 리뷰 수의 로그 변환 적용
        product_analysis['log_reviews'] = np.log1p(product_analysis['average_reviews']) # 총 리뷰수
        # 로그 변환된 리뷰 수를 정규화할 필요가 없으므로, 직접 종합 점수 계산에 포함
        product_analysis['normalized_sentiment'] = product_analysis['positive_sentiment_rate'] * 5
        product_analysis['final_score'] = (
            product_analysis['log_reviews'] / product_analysis['log_reviews'].max() * 1.0 + # 총 리뷰 수! 최대 로그 리뷰 점수로 정규화 
            product_analysis['average_total_rating'] / 5 * 1.5 +  # 총 평점! 5점 만점으로 정규화된 점수 
            product_analysis['average_feature_score'] / 5 * 1.5 +  # Feature Score! 5점 만점으로 정규화된 점수
            product_analysis['normalized_sentiment'] / 5 * 1.0  # 긍정 키워드 감성분석 비율 5점 만점으로 정규화된 점수
        ) #* 10 / (2.0 + 3.0 + 2.0 + 3.0)

        # 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 기준으로 상위 5개 제품 선정
        top_5_products = product_analysis.sort_values(by='final_score', ascending=False).head(5).reset_index(drop=True)
        # top_10_products.to_csv(f'{self.filePath.replace('Raw', 'bestTen')}', encoding='utf-8-sig')
        self.addToExcelSheet(dataFrame=top_5_products, sheetName='best5')
  
        return top_5_products
    
dataAnalysis = DataAnalysis("./results/double_strollers_Raw.csv")
# df_sentiment = dataAnalysis.preprocessorBestTen()
# df_feature_score = dataAnalysis.calScore(df_sentiment)
# df_v2 = pd.read_excel("./results/baby_double_strollers_All.xlsx", 'V2')
# best_ten_products = dataAnalysis.bestTenFirst(df_v2)
# dataAnalysis.preprocessorBestTen()
# df_sentiment = pd.read_excel("./results/double_strollers_All.xlsx", 'sentiment')
df_feature_score = pd.read_excel("./results/double_strollers_All.xlsx", 'finalFeatureScore')
dataAnalysis.bestFive(df_feature_score)
# print(df_feature_score.head())

# df_sentiment['PositivePercentage'] = df_sentiment['PosNegMainFeatures'].apply(lambda x: dataAnalysis.extract_percentage(x, r'(\d+)% of the reviews are positive'))
# df_sentiment['NegativePercentage'] = df_sentiment['PosNegMainFeatures'].apply(lambda x: dataAnalysis.extract_percentage(x, r'(\d+)% of the reviews are negative'))

# print(df_sentiment['PositivePercentage'])
