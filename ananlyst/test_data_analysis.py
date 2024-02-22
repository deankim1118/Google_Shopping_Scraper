import pandas as pd
from textblob import TextBlob
from collections import defaultdict
import re
import numpy as np
# import text_clean
# from PIL import Image
# from wordcloud import WordCloud
# import matplotlib.pyplot as plt
 
class DataAnalysis:
    def __init__(self, filePath = str) -> None:
        self.filePath = "./results/baby_bed_Raw.csv"
        
    
    def preprocessor(self):
        df_raw = pd.read_csv(self.filePath).drop_duplicates(subset=['reviews']).reset_index(drop=True)
        # print(df.info())
        # review_df = df[['product','totalRating','total review','seller','price','features','rating','reviews']]
        df_review = df_raw[['product','url','totalRating','totalReviews','seller','price','features','rating','reviews']]
        
        # seller_df = df[['totalRating','title','features','seller', 'price']].dropna(subset=['totalRating']).reset_index(drop=True)
        # seller_df.to_csv('espresso_machines_price.csv')
        # review_df['ave_reviews'] = review_df['rating'].mean()
        # print(review_df.head())
        # seller_df['price'].astype(float)
        # product_num = review_df.groupby(['product']).count()
        
        # main_Features = df.dropna(subset=['features'])[['product', 'features',]]
        # Split features -> Main Features
        # review_df['main_Features'] = review_df['features'].str.split('(', expand= True)[0]
        # main_Features_df = review_df.groupby(['main_Features'])['product'].describe()
        # main_Features_pivot = pd.pivot_table(review_df, index='product', columns='main_Features', aggfunc='count')
        # review_df.to_csv(f'{self.filePath.replace('Raw', '2')}')
        # 2. 감성분석
        df_sentiment_analysis = self.sentimentAnalysis(df_review)
        # 3. Split Main Features and Percent of Main Features
        df_splitMainFeatures = self.splitMainFeatures(df_sentiment_analysis)
        # 4. Save as csv
        df_splitMainFeatures.to_csv(f'{self.filePath.replace('Raw', 'test')}', encoding='utf-8-sig')
        # 5. Group by Main Features and save as CSV
        self.groupMainFeatures(df_splitMainFeatures)
        # 6. Calculate Score
        self.calScore(df_splitMainFeatures)
        #print(df_splitMainFeatures.head())

        
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
            # if pos_neg == 0:
            #     sentimentAnalysis.append(0)
            # elif pos_neg > 0.5:
            #     sentimentAnalysis.append(2)
            # elif pos_neg > 0 and pos_neg <= 0.5:
            #     sentimentAnalysis.append(1)
            # elif pos_neg < 0 and pos_neg >= -0.5:
            #     sentimentAnalysis.append(-1)
            # else:
            #     sentimentAnalysis.append(-2)
        df_copy = df.copy()
        df_copy['sentimentAnalysis'] = sentimentAnalysis
        df = df_copy.query("sentimentAnalysis != 0")
        
        # test = df.groupby('product')['sentimentAnalysis'].describe()
        return df
        
    def splitMainFeatures(self, df):
        split_features = df['features'].str.split('(', expand= True)
        df['main_features'] = split_features[0]
        num_of_mainFeatures = split_features[1].str.split(')', expand=True)[0].apply(pd.to_numeric, errors='coerce')
        df['totalReviews'] = df['totalReviews'].replace(',', '', regex=True).apply(pd.to_numeric, errors='coerce')
        df['percentOfMainFeatures'] = (num_of_mainFeatures / df['totalReviews'] * 100).round(1)
        pos_neg_mainFeatures = df['features'].str.split('.', expand=True)[1]
        df['PosNegMainFeatures'] = pos_neg_mainFeatures
        # pos_neg_mainFeatures = df['features'].str.split('.', expand=True)[1].str.split('%', expand=True)
        # df['percentPosNeg'] = pos_neg_mainFeatures[0]
        # df['PosNegMainFeatures'] = pos_neg_mainFeatures[1]
        return df
        
    def groupMainFeatures(self, df):
        group_mainFeatures = df.groupby(['main_features','title','PosNegMainFeatures'])['percentOfMainFeatures'].mean()
        group_mainFeatures.to_csv(f'{self.filePath.replace('Raw', 'MainFeatures')}', encoding='utf-8-sig')
     
     # "PosNegMainFeatures" 컬럼에서 긍정 비율 추출 함수
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
    def calScore(self, df):
       
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
                if not feature_df.empty and (feature_df['percentOfMainFeatures'].item() >= 5 or (feature_df['percentOfMainFeatures'].item() >= 3.5 and feature_df['numOfMainFeatures'].item() >= 30) or (feature_df['percentOfMainFeatures'].item() >= 2.5 and not pd.isnull(feature_df['NegativePercentage'].item()) and feature_df['percentOfMainFeatures'].item() >= 5)):
                    # 평균 긍정 및 부정 비율 계산
                    positive_percentage_avg = feature_df['PositivePercentage'].mean()
                    negative_percentage_avg = feature_df['NegativePercentage'].mean()
                    # 주요 기능 비율 계산
                    percent_of_main_features_avg = feature_df['percentOfMainFeatures'].mean()
                    # 점수 계산
                    if not pd.isnull(positive_percentage_avg):
                        positive_score = (positive_percentage_avg / 100) * 5
                    else:
                        positive_score = None
                    
                    if not pd.isnull(negative_percentage_avg):
                        negative_score = 5 - (negative_percentage_avg / 100) * 5
                    else:
                        negative_score = None
                    
                    # 주요 기능 비율을 기반으로 추가 점수 계산 (최대 1점 추가)
                    additional_score = (percent_of_main_features_avg / 100) * 1
                    # 종합 점수 계산: 기본 점수 + 추가 점수
                    if positive_score != None:
                        final_score = positive_score + additional_score
                    elif negative_score != None:
                        final_score = negative_score - additional_score
                    # 점수를 5점 만점으로 제한
                    final_score = min(final_score, 5)
                    # 결과 저장
                    product_feature_scores[product][feature] = {
                        'PositiveScore': positive_score,
                        'NegativeScore': negative_score,
                        'FinalScore': round(final_score, 2),
                        'PosNegPercentage' : feature_df['percentOfMainFeatures'].mean(),
                    }
        # DataFrame으로 변환
        results = []
        for product, features in product_feature_scores.items():
            for feature, scores in features.items():
                results.append({
                    'Product': product,
                    'Feature': feature,
                    'PositiveScore': scores['PositiveScore'],
                    'NegativeScore': scores['NegativeScore'],
                    'FinalScore': scores['FinalScore'],
                    'PosNegPercentage' : scores['PosNegPercentage'],
                })
        df_score = pd.DataFrame(results)
        # Add the "Easy to use score" to the DataFrame
        df_score.to_csv(f'{self.filePath.replace('Raw', 'Score_test')}', encoding='utf-8-sig')
                    
        print(df_score.head())

        # # 결과 출력 (모든 제품에 대한 출력은 과도할 수 있으므로 첫 2개 제품의 결과만 예시로 보여줍니다)
        # for product, features_scores in list(product_feature_scores.items())[:2]:
        #     print(f"Product: {product}")
        #     for feature, score in features_scores.items():
        #         print(f"  - {feature}: {score:.2f}점")
        #     print("\n")
        
    def bestTenProducts(self):
                # 데이터 파일 경로
        file_path = './results/baby_stroller_test.csv'

        # 데이터 불러오기
        data = pd.read_csv(file_path)

        # 'positive_sentiment' 컬럼 추가: 1은 긍정, -1은 부정
        data['positive_sentiment'] = data['sentimentAnalysis'].apply(lambda x: 1 if x == 1 else 0)

        # 각 제품별로 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 계산
        product_analysis = data.groupby(['product']).agg(
            average_total_rating=('totalRating', 'mean'),
            average_reviews=('totalReviews', 'mean'),
            average_rating=('rating', 'mean'),
            positive_sentiment_rate=('positive_sentiment', 'mean')
        ).reset_index()
        
        # 리뷰 수의 로그 변환 적용
        product_analysis['log_reviews'] = np.log1p(product_analysis['average_reviews'])
        # 로그 변환된 리뷰 수를 정규화할 필요가 없으므로, 직접 종합 점수 계산에 포함
        product_analysis['normalized_sentiment'] = product_analysis['positive_sentiment_rate'] * 5
        product_analysis['final_score'] = (
            product_analysis['average_total_rating'] / 5 * 2.0 +  # 5점 만점으로 정규화된 점수
            product_analysis['average_rating'] / 5 * 2.0 +  # 5점 만점으로 정규화된 점수
            product_analysis['normalized_sentiment'] / 5 * 3.0 +  # 5점 만점으로 정규화된 점수
            product_analysis['log_reviews'] / product_analysis['log_reviews'].max() * 3.0  # 최대 로그 리뷰 점수로 정규화
        ) * 10 / (2.0 + 2.0 + 3.0 + 3.0) 
        # # 점수 계산 로직 구현
        # product_scores = product_analysis.copy()
        # product_scores['score'] = (
        #     product_scores['average_total_rating'] * 2 +  # 평균 총 평점에 더 큰 가중치 부여
        #     product_scores['average_rating'] * 1.5 +  # 평균 개별 평점에 가중치 부여
        #     product_scores['positive_sentiment_rate'] * 1.5  # 긍정적 감성 비율에 가중치 부여
        # ) / 5

        # 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 기준으로 상위 5개 제품 선정
        top_10_products = product_analysis.sort_values(by=['positive_sentiment_rate','average_total_rating', 'average_rating', 'average_reviews'], ascending=False).head(10)
        top_10_products_log = product_analysis.sort_values(by='final_score', ascending=False).head(10)
        # 'average_reviews'는 추가 점수로 반영할 수 있으나, 직접적인 점수 계산에는 포함되지 않음
        # top_5_scored_products = product_scores.sort_values(by='score', ascending=False).head(10)
        top_10_products_log.to_csv(f'{self.filePath.replace('Raw', 'bestTen')}', encoding='utf-8-sig')
    
    def bestTenFirst(self, df):
        # PosNegMainFeatures에서 긍정 리뷰의 비율을 숫자로 변환
        df_score = df.copy()
        df_score['positive_review_percentage'] = df_score['PosNegMainFeatures'].apply(lambda x: float(x.split('%')[0]) if "positive" in x else None)
        df_score = df_score.dropna(subset=['positive_review_percentage']).reset_index(drop=True)
        # data['score'] = data.apply(lambda x: ((x['percentOfMainFeatures'] / 100) * 2.5 + (x['positive_review_percentage'] / 100) * 2.5) if pd.notnull(x['positive_review_percentage']) else 0, axis=1)
        # 각 제품별로 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 계산
        product_analysis = df_score.groupby(['title', 'url']).agg(
            average_total_rating=('totalRating', 'mean'),
            average_reviews=('totalReviews', 'mean'),
            average_percentOfMainFeatures=('percentOfMainFeatures', 'mean'),
            positive_positive_review_percentage=('positive_review_percentage', 'mean')
        ).reset_index()
        
        # 리뷰 수의 로그 변환 적용
        product_analysis['log_reviews'] = np.log1p(product_analysis['average_reviews']) # 총 리뷰수
        # 로그 변환된 리뷰 수를 정규화할 필요가 없으므로, 직접 종합 점수 계산에 포함
        product_analysis['final_score'] = (
            product_analysis['average_total_rating'] / 5 * 1.0 +  # 총 평점! 5점 만점으로 정규화된 점수 
            product_analysis['average_percentOfMainFeatures'] / product_analysis['average_percentOfMainFeatures'].max() * 1.5 +  # 긍정 키워드 비율 5점 만점으로 정규화된 점수
            product_analysis['positive_positive_review_percentage'] / 100 * 1.0 +  # 긍정 키워드 감성분석 비율 5점 만점으로 정규화된 점수
            product_analysis['log_reviews'] / product_analysis['log_reviews'].max() * 1.5  # 최대 로그 리뷰 점수로 정규화
        ) #* 10 / (2.0 + 3.0 + 2.0 + 3.0)

        # 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 기준으로 상위 5개 제품 선정
        top_10_products = product_analysis.sort_values(by='final_score', ascending=False).head(10)
        ## top_10_products.to_csv(f'{self.filePath.replace('Raw', 'bestTen')}', encoding='utf-8-sig')
        print(type(top_10_products['url']))
        
        
    # def wordCloudReviews(self):
    #         data_path = './results/baby_stroller_V2.csv'
    #         stroller_data = pd.read_csv(data_path)

    #         # 각 고유 제품에 대한 리뷰들을 추출합니다.
    #         reviews_by_product = stroller_data.groupby('product')['reviews'].apply(lambda x: ' '.join(x)).reset_index()
    #         text_reviews = text_clean.clean(reviews_by_product['reviews'][0])
    #         # 결과를 출력합니다.
    #         #print(len(text_reviews))
    #         wc = WordCloud().generate(text_reviews)
    #         plt.imshow(wc)
    #         plt.show()
            
    def printTest(self):
        df = pd.read_csv("./results/baby_stroller_V2.csv")
        df_mainFeatures = pd.read_csv("./results/baby_stroller_MainFeatures.csv")
        print(df.info())
        
dataAnalysis = DataAnalysis()
# dataAnalysis.preprocessor()
# dataAnalysis.printTest()
df = pd.read_csv("./results/baby_bed_V2.csv")
dataAnalysis.bestTenFirst(df)
# dataAnalysis.wordCloudReviews()
# dataAnalysis.bestTenProducts()

