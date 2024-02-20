import pandas as pd
# from google_Shop_Scraper.utilites.baseClass import BaseClass

# class TestDataFrame():
#     def test_data_frame(self):
#         pass

test = [{"title": "nike", 
         "rating": 4.5, 
         "review": "Good",
         },
        {"title": "adidas", 
         "rating": 2.4, 
         "review": "Bad",
         },
        {"title": "Chanel", 
         "rating": 4.8, 
         "review": "Excellent"
         ,},
        {"title": "Boss", 
         "rating": 4.7, 
         "review": "Excellent"
         ,}]

df = pd.DataFrame(test)

# print(df["rating"].mean())
# print(df.shape) # Row, Column 갯수
# print(df.info())
# print(df.describe())
# print(df.isnull().sum())
# print(df.columns)
# print(df["rating"].values)
# print(df.index.values)


# df.to_csv('test.csv', index=True, encoding='utf-8')
# print(df)
# print(df.iloc[-1]) #Get Specific Row data
# print(df.sort_values(by="rating", ascending=False)) #내림차순 정렬! Dafault = 오름차순 정렬
#print(df["rating"].value_counts())
# condition = df["rating"] >= 4
# df = df.loc[condition] , df.loc[Row, Columns]
# print(df)

## 밑의 식과 같다. 필터링
# df = df[(df["rating"] > 4) & (df["review"] == "Excellent")]
# df = df.query("rating > 4 and review == 'Excellent'")
print(df.reset_index(drop=True))