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
    df2["min_grade"] = df2["min_grade"].apply(EnumManipulation.convert_to_enum_value)
    df2["max_grade"] = df2["max_grade"].apply(EnumManipulation.convert_to_enum_value)
    
    uniq_pages = df2["worksheet_uid"].unique()
    
    df = pd.DataFrame(dbAPI.get_all_pages_topics(), columns=["worksheet_uid", "topic"])
    
    # df = pd.merge(df2, df, on=["worksheet_uid"], how='left')
    #TODO interogate if its better with not merge

    uniq_topics = df["topic"].unique()
    
    zeroes_df = pd.DataFrame(0, index=uniq_pages, columns=np.concatenate((uniq_topics, np.array(range(12)))))

    for _, row in df.iterrows():
        if row["worksheet_uid"] in zeroes_df.index:
            zeroes_df.loc[row["worksheet_uid"], row["topic"]] = 1
    del df
        
    for _, row in df2.iterrows():
        for val in range(row["min_grade"], row["max_grade"]+1):
            zeroes_df.loc[row["worksheet_uid"], val] = 1
    del df2
    
    cos_sim = cosine_similarity(zeroes_df.values)
    
    # print("0ba2893f\n", zeroes_df.loc["0ba2893f", zeroes_df.loc["0ba2893f"] != 0])
    
    # print("0a810afe\n", zeroes_df.loc["0a810afe", zeroes_df.loc["0a810afe"] != 0])
    
    # print("00d74576\n", zeroes_df.loc["00d74576", zeroes_df.loc["00d74576"] != 0])

    cos_sim_df = pd.DataFrame(cos_sim, index=zeroes_df.index, columns=zeroes_df.index)
    del zeroes_df
    # print("0ba2893f", cos_sim_df.loc["0a810afe","0ba2893f"])
    # print("00d74576", cos_sim_df.loc["0a810afe","00d74576"])
    
    return cos_sim_df

def top_n_cos_sim(df: pd.DataFrame, n):

    top_10_df = pd.DataFrame({"worksheet_uid": df.index},index=df.index)
    top_10_df["top_10"] = ''
    
    # print(df.loc["0a810afe","00d74576"])
    # print(df.loc["0a810afe","0ba2893f"])

    for index, row in df.iterrows():
        sorted = row.sort_values(ascending=False)
        # if index == "0a810afe":
        #     sorted.to_csv("/Users/nivdavidian/Downloads/sorted.csv")
        #     print(sorted.head(n).index.to_list())
        top_10_df.loc[index, "top_10"] = ','.join(sorted.head(n).index.to_list())

    return top_10_df

def analyze_interactive(c_code, l_code, step=5):
    res = dbAPI.get_interactive_by_clcodes(c_code, l_code)
    if res == None or len(res) == 0:
        print("something went wrong")
    
    df_o = pd.DataFrame(res, columns=["user_uid", "worksheet_uid", "l_code", "c_code", "time"])
    
    df_o["time"] = pd.to_datetime(df_o["time"], format="%Y-%m-%d %H:%M:%S")
    df_o = df_o.sort_values(by=['user_uid', 'time'], ascending=[False, False])
    # if l_code == 'he':
    #     df_o.to_csv('ddd.csv')
    
    df = df_o.drop(columns=["c_code", "l_code", "time"])
    
    groupby = df.groupby(by="user_uid")
    df2 = groupby.nunique().rename(columns={"worksheet_uid": "count"})
    df2 = df2[df2["count"]>1]
    
    d2 = groupby.apply(lambda group: [i for i in group["worksheet_uid"]], include_groups=False).to_frame().reset_index()
    d2.columns = ['user_uid', "worksheets"]
    d2 = d2[d2['user_uid'].isin(df2.index)].reset_index(drop=True)
    n = step*2
    d2['worksheets'] = d2['worksheets'].apply(lambda g: [g[i*step:min(len(g),i*step+n)] for i in range(int(len(g)/step) if len(g)>=step else 1)] + [g])
    d2 = d2.explode('worksheets').reset_index(drop=True)
    def get_index(size):
        for i in range(size):
            yield i
    
    gen = get_index(d2.size)
    d2["original_uid"] = d2["user_uid"]
    d2['user_uid'] = d2['user_uid'].apply(lambda uid: f"{next(gen)}_{uid}")
    
    os.makedirs("./user_worksheets_indexes", exist_ok=True)
    d2.to_parquet(f"./user_worksheets_indexes/{c_code}-{l_code}.parquet")
    # if l_code == "he":
    #     d2.to_csv(f"./user_worksheets_indexes/{c_code}-{l_code}.csv")
    
    df = df.groupby(by="worksheet_uid").apply(lambda group: ",".join(group["user_uid"]), include_groups=False)
    df.name = "users"
    df = pd.DataFrame(df)
    
    os.makedirs("./worksheet_users_indexes", exist_ok=True)
    df.to_parquet(f"./worksheet_users_indexes/{c_code}-{l_code}.parquet")
    # df.to_csv(f"./worksheet_users_indexes/{c_code}-{l_code}.csv")
    
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
    # print(df.head(3))
    df = df.groupby(by=["worksheet_uid1", "worksheet_uid2"]).mean().rename(columns={"time": "mean"}).sort_values(by="mean", ascending=True).reset_index()
    df = df[(df["mean"]>0) & (df["mean"]<100)]
    df.to_csv("111.csv")
    # print(df.head(3))
    
def markov(c_code, l_code):
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
    df = df[df["time"]<2]
    # print(df.head(3))
    df = df.groupby(by=["worksheet_uid1", "worksheet_uid2"], sort=False).count().rename(columns={"time": "count"})
    df = df.sort_values("count", ascending=False)
    df['count'] = df["count"]/df["count"].max()
    df = df.groupby(by='worksheet_uid1',sort=False).apply(lambda g: [[data['worksheet_uid2'], data['count']] for _, data in g.iterrows()])
    df.to_csv("111.csv")
    # print(df.head(3))
    
def popular_in_month(c_code, l_code):
    res = dbAPI.get_interactive_by_clcodes(c_code, l_code)
    if res == None or len(res) == 0:
        print("something went wrong")
    df = pd.DataFrame(res, columns=["user_uid", "worksheet_uid", "l_code", "c_code", "time"]).drop_duplicates().reset_index(drop=True)
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
    
    top_n_df.to_parquet(f"{path}/{l_code}-{c_code}.parquet", index=False)
    # cos_df.to_parquet(f'cos_sim_files/{l_code}-{c_code}.parquet', index=False)
    print(f"finished {l_code}-{c_code}")
