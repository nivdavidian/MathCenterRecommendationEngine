import pandas as pd
import json
import dbAPI
import numpy as np
import os

from enum import Enum
from sklearn.metrics.pairwise import cosine_similarity

class Grade(Enum):
    prek = 0
    kindergarten = 1
    first = 2 
    second = 3
    third = 4
    fourth = 5
    fifth = 6
    sixth = 7
    seventh = 8
    eighth = 9
    ninth = 10
    tenth = 11

class EnumManipulation:
    str_to_enum_value_map = {
            "pre-k": 0,
            "kindergarten": 1,
            "1st": 2,
            "2nd": 3,
            "3rd": 4,
            "4th": 5,
            "5th": 6,
            "6th": 7,
            "7th": 8,
            "8th": 9,
            "9th": 10,
            "10th": 11
            }
    @classmethod
    def convert_to_enum_value(cls, grade_str):
        return cls.str_to_enum_value_map[grade_str]
    
    @classmethod
    def enum_names_by_value(cls, values):
        names = []
        for value in values:
            names.append(Grade(value).name)
        
        return names
    
    @classmethod
    def isin(cls, min_grade, max_grade, isin):
        min_grade = cls.convert_to_enum_value(min_grade)
        max_grade = cls.convert_to_enum_value(max_grade)
        
        if isin >= min_grade and isin <= max_grade:
            return True
        else:
            return False
    
    

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


def analyze_downloads():
    res = dbAPI.get_all_user_downloads()
    df3 = pd.DataFrame(res, columns=["user_uid", "country_code", "language_code", "downloads"])

    df3["downloads"] = df3["downloads"].apply(lambda x: list(json.loads(x[1:-1])))
    df3 = df3.explode("downloads").reset_index(drop=True)
    df3["worksheet_uid"] = df3["downloads"].apply(lambda x: x["pageUid"])
    df3["downloads"] = pd.to_datetime(df3["downloads"].apply(lambda x: x["time"]), utc=True)

    rows_to_remove = []

    for index, row in df3.iterrows():
        if index + 1 < len(df3):
            next_row = df3.iloc[index + 1]
            if row['user_uid'] == next_row['user_uid'] and row['worksheet_uid'] == next_row['worksheet_uid']:
                rows_to_remove.append(index)

    df3 = df3.drop(rows_to_remove).reset_index(drop=True)

    df3["year"] = df3["downloads"].dt.year
    df3["month"] = df3["downloads"].dt.month
    df3["day"] = df3["downloads"].dt.day

    df3 = df3.drop(columns=['downloads', 'user_uid', 'day', 'year'])

    df3 = df3[["country_code", "language_code", "worksheet_uid", "month"]]
    df3.drop_duplicates()

#Calculates the cosine similarity between worksheet vectors based on topics and grade levels. This is useful for finding similar worksheets.
def calculate_cos_sim_by_country(c_code, l_code):
    
    df2 = pd.DataFrame(dbAPI.get_worksheet_grades_by_country_lang(c_code, l_code), columns=["worksheet_uid", "min_grade", "max_grade"])
    
    df = pd.DataFrame(dbAPI.get_all_pages_topics(), columns=["worksheet_uid", "topic"])
    df = pd.get_dummies(df, columns=['topic'], prefix="", prefix_sep="").groupby(by='worksheet_uid').any()
    df = pd.merge(df2, df, on='worksheet_uid', how='left')
    df['grades'] = df.apply(lambda x: EnumManipulation.enum_names_by_value(list(range(EnumManipulation.convert_to_enum_value(x['min_grade']), EnumManipulation.convert_to_enum_value(x['max_grade'])+1))), axis=1)
    df = df.drop(columns=['min_grade', 'max_grade']).explode('grades')
    
    df = pd.get_dummies(df, columns=['grades'], prefix="", prefix_sep="").groupby(level=0).max()
    df = df.set_index('worksheet_uid')
    # pd.get_dummies(pd.merge(df2, df, on=["worksheet_uid"], how='left').set_index('worksheet_uid', inplace=False).head(1000)).to_csv('111.csv')
    #TODO interogate if its better with not merge
    # df.to_csv(f"top_by_country_files/{l_code}-{c_code}.csv", index=True)

    
    cos_sim = cosine_similarity(df.values)
    
    # print("0ba2893f\n", zeroes_df.loc["0ba2893f", zeroes_df.loc["0ba2893f"] != 0])
    
    # print("0a810afe\n", zeroes_df.loc["0a810afe", zeroes_df.loc["0a810afe"] != 0])
    
    # print("00d74576\n", zeroes_df.loc["00d74576", zeroes_df.loc["00d74576"] != 0])

    cos_sim_df = pd.DataFrame(cos_sim, index=df.index, columns=df.index)
    # print("0ba2893f", cos_sim_df.loc["0a810afe","0ba2893f"])
    # print("00d74576", cos_sim_df.loc["0a810afe","00d74576"])
    
    return cos_sim_df

def top_n_cos_sim(df: pd.DataFrame, n):
    df = df.apply(lambda row: json.dumps(list(row.loc[(row.index!=row.name) & (row>=0.4)].sort_values(ascending=False,).items())), axis=1)
    df.name = 'top_10'
    df = df.to_frame()
    return df

def interactive_user_similarity_analysis(data: pd.DataFrame, step, c_code, l_code):
    data = data.drop_duplicates().reset_index(drop=True)
    data["time"] = pd.to_datetime(data["time"], format="%Y-%m-%d %H:%M:%S")
    
    data = data.sort_values(by=['user_uid', 'time'], ascending=[False, True])
    
    data['date'] = data["time"].dt.strftime('%Y-%m-%d %H')
    data = data.drop_duplicates(subset=['user_uid', 'worksheet_uid', 'date'], keep='first')[['user_uid', 'worksheet_uid', 'time']]
    
    df2 = data.groupby(by='user_uid', sort=False, group_keys=False).count()
    df2 = df2[df2['worksheet_uid']>1]
    data = data[data['user_uid'].isin(df2.index)].reset_index(drop=True)
    
    n=step*2
    data = data.groupby(by='user_uid')[['worksheet_uid']].apply(lambda g: ([list(g['worksheet_uid'])] + [g['worksheet_uid'].to_list()[i*step:min(len(g['worksheet_uid'].to_list()),i*step+n)] for i in range(int(len(g["worksheet_uid"].to_list())/step) if len(g["worksheet_uid"].to_list())>n else 0)]))
    data = data.explode().reset_index()
    data['user_uid'] = [f"{i}_" for i in data.index] + data['user_uid']
    data = data.explode(0)
    
    os.makedirs("./UserSimilarityParquets", exist_ok=True)
    data.to_parquet(f'UserSimilarityParquets/{l_code}.parquet', index=False)
    # data.to_csv(f'UserSimilarityParquets/{c_code}-{l_code}.csv', index=False)
    
def difference_in_mean(c_code, l_code):
    res = dbAPI.get_interactive_by_clcodes(c_code, l_code)
    if res == None or len(res) == 0:
        print("something went wrong")
    
    df = pd.DataFrame(res, columns=["user_uid", "worksheet_uid", "l_code", "c_code", "time"]).drop_duplicates().reset_index(drop=True)
    df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
    df = df.drop(["c_code", "l_code"], axis=1)
    
    df = pd.merge(df, df, on="user_uid", suffixes=["1","2"])
    df = df[df["worksheet_uid1"]!=df["worksheet_uid2"]]
    df["time"] = (df["time1"] - df["time2"]).apply(lambda x: abs(x.days))
    df = df.drop(columns=["time1", "time2", "user_uid"])
    df2 = df.groupby(by=['worksheet_uid1', 'worksheet_uid2'], group_keys=False).count().rename(columns={"time": "count"}).reset_index()
    
    df = df.groupby(by=["worksheet_uid1", "worksheet_uid2"], group_keys=False)[['time']].apply(lambda g: g['time'].mean()+1/(1+g["time"].size)).reset_index().rename(columns={0: "mean"})
    df = df[df2['count']>=20]
    print(df.head(3))
    df = df.sort_values(by="mean", ascending=True)
    df = df[(df["mean"]>0) & (df["mean"]<100)]
    df.to_csv("222.csv")
    # print(df.head(3))
    
def markov(df: pd.DataFrame, c_code, l_code):
    # print(df.head(10))
    df = df.drop_duplicates().reset_index(drop=True)
    
    df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
    # df = df.drop(["c_code", "l_code"], axis=1)
    df = df.sort_values(by=['user_uid', 'time'], ascending=[True, True])
    df['count'] = 0
    df2 = df.groupby(by=['user_uid'], group_keys=False)[['count']].count().reset_index()
    df2 = df2[df2['count']>1]
    
    df = df[df['user_uid'].isin(df2['user_uid'])]
    df = df.drop(columns=['count', 'c_code', 'l_code'])
    df = pd.concat([df, df.shift(-1).rename(columns={"user_uid": "user_uid_1", "worksheet_uid": "worksheet_uid_1", "time": "time_1"})], axis=1)
    df = df[(df["user_uid"]==df["user_uid_1"]) & (df["worksheet_uid"]!=df["worksheet_uid_1"]) & (df["time_1"]-df["time"]<pd.Timedelta(days=30))].reset_index(drop=True)
    # df.to_csv("ar.csv")
    df = df.drop(['user_uid_1', 'user_uid', 'time'], axis=1)
    df = df.groupby(by=['worksheet_uid', 'worksheet_uid_1'], group_keys=False).count().rename(columns={'time_1':'count'}).reset_index()
    
    df = df.sort_values(by=['worksheet_uid', 'count'], ascending=[False,False]).set_index('worksheet_uid')
    
    os.makedirs('MarkovModelParquets', exist_ok=True)
    df.to_parquet(f"MarkovModelParquets/{l_code}.parquet")
    # df[['user_uid', 'user_uid_1', 'worksheet_uid','worksheet_uid_1','time','time_1']].to_csv(f"MarkovModelParquets/{c_code}-{l_code}.csv")
    
def popular_in_month(df, c_code, l_code):
    
    df = df.drop_duplicates().reset_index(drop=True)
    df["month"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S").apply(lambda x: x.month)
    df = df.drop(columns=["c_code", "l_code", "user_uid", "time"])
    df['count'] = 0
    df = df.groupby(by=['worksheet_uid', 'month'], sort=False).count().reset_index().sort_values(by=['month', 'count'], ascending=[True, False])
    
    df2 = pd.DataFrame(dbAPI.get_worksheet_grades_by_uids(df['worksheet_uid'].unique(), c_code, l_code), columns=['worksheet_uid', 'min_grade', 'max_grade'])
    
    df = pd.merge(df, df2, on='worksheet_uid')
    df['grades'] = df.apply(lambda x: EnumManipulation.enum_names_by_value(list(range(EnumManipulation.convert_to_enum_value(x['min_grade']), EnumManipulation.convert_to_enum_value(x['max_grade'])+1))), axis=1)
    df = df.drop(columns=['min_grade', 'max_grade']).explode('grades')
    
    df = pd.get_dummies(df, columns=['grades'], prefix="", prefix_sep="").groupby(level=0).max()
    os.makedirs('most_populars', exist_ok=True)
    df.to_parquet(f"most_populars/{c_code}-{l_code}.parquet")

def task(c_code, l_code, n):
    cos_df = calculate_cos_sim_by_country(c_code, l_code)
    top_n_df = top_n_cos_sim(cos_df, n)
    
    # directory_path = 'cos_sim_files'
    # os.makedirs(directory_path, exist_ok=True)
    
    path = "top_by_country_files"
    os.makedirs(path, exist_ok=True)
    
    top_n_df.to_parquet(f"{path}/{l_code}-{c_code}.parquet", index=True)