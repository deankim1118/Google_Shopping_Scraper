from collections import defaultdict
import re
import numpy as np
import pandas as pd
from textblob import TextBlob
 
class DataAnalysis:
    def __init__(self, filePath = str) -> None:
        self.filePath = filePath
        # self.filePath = "./results/baby_stroller_Raw.csv"
        
    
    def preprocessor(self):      
        """ 1. Review 제외하고 main_features.csv에서 (totalRating,totalReviews,PosNegMainFeatures,percentOfMainFeatures)로 Best 10 뽑기
            2. Scraping Best10 Reviews & ratings
            3. Best10 Sentiment Analysis
            4. 1번 방법 + ratings.mean() + sentiment.mean() 으로 Best5 뽑기
            5. best5의 main_features 점수, Negative Review Percents.
        """
        df_raw = pd.read_csv(self.filePath).drop_duplicates(subset=['reviews']).reset_index(drop=True)
        # 1. Set Columns that are only used
        df_review = df_raw[['title','url','seller','price','totalRating','totalReviews','features']]
        # 2. 감성분석
        df_sentiment_analysis = self.sentimentAnalysis(df_review)
        # 3. Split Main Features and Percent of Main Features
        df_v2 = self.splitMainFeatures(df_sentiment_analysis)
        # 4. Save as csv
        df_v2.to_csv(f'{self.filePath.replace('Raw', 'V2')}', encoding='utf-8-sig')
        # 5. Group by Main Features and save as CSV
        df_mainFeatures = self.groupMainFeatures(df_v2)
        # 6. Pick Best 10 Products
        self.bestTenProducts(df_v2)
        # 7. Caculate scores by Main Features
        self.calScore(df_v2)
        
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
        df = df_copy.query("sentimentAnalysis != 0")

        return df
        
    def splitMainFeatures(self, df):
        split_features = df['features'].str.split('(', expand= True)
        df['main_features'] = split_features[0]
        num_of_mainFeatures = split_features[1].str.split(')', expand=True)[0].apply(pd.to_numeric, errors='coerce')
        df['totalReviews'] = df['totalReviews'].replace(',', '', regex=True).apply(pd.to_numeric, errors='coerce')
        df['numOfMainFeatures'] = num_of_mainFeatures
        df['percentOfMainFeatures'] = (num_of_mainFeatures / df['totalReviews'] * 100).round(1)
        pos_neg_mainFeatures = df['features'].str.split('.', expand=True)[1]
        df['PosNegMainFeatures'] = pos_neg_mainFeatures
        # pos_neg_mainFeatures = df['features'].str.split('.', expand=True)[1].str.split('%', expand=True)
        # df['percentPosNeg'] = pos_neg_mainFeatures[0]
        # df['PosNegMainFeatures'] = pos_neg_mainFeatures[1]
        return df
        
    def groupMainFeatures(self, df):
        # group_mainFeatures = df.groupby(['main_features','product','PosNegMainFeatures'])['percentOfMainFeatures'].mean()
        # group_mainFeatures.to_csv(f'{self.filePath.replace('Raw', 'MainFeatures')}', encoding='utf-8-sig')
        group_mainFeatures = df.groupby(['main_features','product','PosNegMainFeatures','totalRating','totalReviews','numOfMainFeatures'])['percentOfMainFeatures'].mean()
        group_mainFeatures.to_csv(f'{self.filePath.replace('Raw', 'MainFeatures')}', encoding='utf-8-sig')
        return group_mainFeatures
        
    def bestTenProducts(self, df):
        # 'positive_sentiment' 컬럼 추가: 1은 긍정, -1은 부정
        df['positive_sentiment'] = df['sentimentAnalysis'].apply(lambda x: 1 if x == 1 else 0)

        # 각 제품별로 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 계산
        product_analysis = df.groupby(['product','url']).agg(
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
        # 평균 총 평점, 총 리뷰 수, 긍정적 감성 비율을 기준으로 상위 10개 제품 선정
        top_10_products_log = product_analysis.sort_values(by='final_score', ascending=False).head(10)
        # Save to file
        top_10_products_log.to_csv(f'{self.filePath.replace('Raw', 'bestTen')}', encoding='utf-8-sig')
        
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
                        positive_score = (positive_percentage_avg / 100) * 4.5
                    else:
                        positive_score = None
                    
                    if not pd.isnull(negative_percentage_avg):
                        negative_score = 5 - (negative_percentage_avg / 100) * 4.5
                    else:
                        negative_score = None
                    
                    # 주요 기능 비율을 기반으로 추가 점수 계산 (최대 1점 추가)
                    additional_score = (percent_of_main_features_avg / 100) * 3
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
        df_score.to_csv(f'{self.filePath.replace('Raw', 'ScoreByFeature')}', encoding='utf-8-sig')
                    
        print(df_score.info())

        # # 결과 출력 (모든 제품에 대한 출력은 과도할 수 있으므로 첫 2개 제품의 결과만 예시로 보여줍니다)
        # for product, features_scores in list(product_feature_scores.items())[:2]:
        #     print(f"Product: {product}")
        #     for feature, score in features_scores.items():
        #         print(f"  - {feature}: {score:.2f}점")
        #     print("\n")
        
        """필요시 moveToEachPage()로 Best5 URL and average_review 이용해서 모든 review 가져와서 분석하는 함수 만들기!"""
        
# dataAnalysis = DataAnalysis()
# dataAnalysis.preprocessor()