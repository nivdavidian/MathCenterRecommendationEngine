import pandas as pd
import json
import datetime
import dbAPI
import numpy as np
import os
import sql_pool

from enum import Enum
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor

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
    
    def __init__(self) -> None:
        self.str_to_enum_value_map = {
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
    
    def convert_to_enum_value(self, grade_str):
        return self.str_to_enum_value_map[grade_str]
    
    def enum_names_by_value(self, values):
        names = []
        for value in values:
            names.append(Grade(value).name)
        
        return names
    
    

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Specify the directory
directory_path = 'cos_sim_files'

# Create the directory if it does not exist
os.makedirs(directory_path, exist_ok=True)

# file_path = os.path.join(directory_path, 'example_file.txt')
# Create a file in the newly created directory
# with open(file_path, 'w') as file:
#     file.write('Hello, world!')



def calculate_cos_sim_by_topics():
    # res = dbAPI.get_all_user_downloads()
    # df = pd.DataFrame(res, columns=["country_code", "language_code", "downloads"])
    # ids = range(len(df))

    # df['user_uid'] = ids

    # df["downloads"] = df["downloads"].apply(lambda x: list(json.loads(x[1:-1])))
    # df = df.explode("downloads").reset_index(drop=True)
    # df["page_uid"] = df["downloads"].apply(lambda x: x["pageUid"])
    # df["downloads"] = pd.to_datetime(df["downloads"].apply(lambda x: x["time"]), utc=True)

    # rows_to_remove = []

    # for index, row in df.iterrows():
    #     if index + 1 < len(df):
    #         next_row = df.iloc[index + 1]
    #         if row['user_uid'] == next_row['user_uid'] and row['page_uid'] == next_row['page_uid']:
    #             rows_to_remove.append(index)

    # df = df.drop(rows_to_remove).reset_index(drop=True)

    # df["year"] = df["downloads"].dt.year
    # df["month"] = df["downloads"].dt.month
    # df["day"] = df["downloads"].dt.day

    # df = df.drop(columns=['downloads'])

    # df = df[["user_uid", "country_code", "language_code", "page_uid", "day", "month", "year"]]

    #Getting all worksheet grades and turns them to data frame
    # df2 = pd.DataFrame(dbAPI.get_all_worksheet_grades(), columns = ["country_code", "language_code", "page_uid", "min_grade", "max_grade"])

    #join grades and downloads
    # df = pd.merge(df, df2, on=["page_uid", "country_code", "language_code"])

    #Group By page Count
    # grouped = df.groupby("page_uid").size().reset_index(name="count").sort_values(by="count", ascending=False).reset_index(drop=True)

    #Group by country, page_id and count
    # def top_10(group):
    #     return group.nlargest(100, 'count')

    # Group by 'country_code' and 'page_uid', count occurrences, and then select the top 10 counts from each country
    # grouped = (df.groupby(["country_code", "page_uid"])
    #            .size()
    #            .reset_index(name="count")
    #            .groupby("country_code")
    #            .apply(top_10)
    #            .reset_index(drop=True))


    # grouped = (df.groupby(["country_code", "page_uid", "month"])
    #         .size()
    #         .reset_index(name="count")
    #         .sort_values(by=["country_code", "month", "count"], ascending=[True, True, False]))
            
    df3 = pd.DataFrame(dbAPI.get_all_pages_topics(), columns=["worksheet_uid", "topic"])

    uniqs = df3["topic"].unique()
    uniq_pages = df3["worksheet_uid"].unique()

    zeroes_df = pd.DataFrame(0, index=range(len(uniq_pages)), columns=range(len(uniqs)))
    zeroes_df.columns = uniqs
    zeroes_df.index = uniq_pages

    for _, row in df3.iterrows():
        zeroes_df.loc[row["worksheet_uid"], row["topic"]] = 1

    cos_sim = cosine_similarity(zeroes_df.values)

    cos_sim_df = pd.DataFrame(cos_sim, index=zeroes_df.index, columns=zeroes_df.index)
    
    return cos_sim_df

def calculate_cos_sim_country_language_topics():
    df = pd.DataFrame(dbAPI.get_all_pages_topics(), columns=["worksheet_uid", "topic"])

    uniq_topics = df["topic"].unique()
    uniq_pages = df["worksheet_uid"].unique()
    
    t = datetime.datetime.now()
    df2 = pd.DataFrame(dbAPI.get_all_worksheet_grades(), columns = ["country_code", "language_code", "worksheet_uid", "min_grade", "max_grade"])
    print(datetime.datetime.now()-t)
    df2["cl_code"] = [f"{row["language_code"]}-{row["country_code"]}" for _, row in df2.iterrows()]
    print(datetime.datetime.now()-t)
    df2.drop(columns=["language_code", "country_code", "min_grade", "max_grade"])
    
    uniq_cl_codes = df2["cl_code"].unique()
    
    extended = np.concatenate((uniq_topics, uniq_cl_codes))
    zeroes_df = pd.DataFrame(0, index=uniq_pages, columns=extended)
    print(datetime.datetime.now()-t)

    for _, row in df.iterrows():
        zeroes_df.loc[row["worksheet_uid"], row["topic"]] = 1
    
    for _, row in df2.iterrows():
        zeroes_df.loc[row["worksheet_uid"], row["cl_code"]] = 1
    
    print(datetime.datetime.now()-t)

    cos_sim = cosine_similarity(zeroes_df.values)

    cos_sim_df = pd.DataFrame(cos_sim, index=zeroes_df.index, columns=zeroes_df.index)
    
    return cos_sim_df

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

def calculate_cos_sim_by_country(c_code, l_code):
    enum_man = EnumManipulation()
    
    df2 = pd.DataFrame(dbAPI.get_worksheet_grades_by_country_lang(c_code, l_code), columns=["worksheet_uid", "min_grade", "max_grade"])
    df2["min_grade"] = df2["min_grade"].apply(enum_man.convert_to_enum_value)
    df2["max_grade"] = df2["max_grade"].apply(enum_man.convert_to_enum_value)
    
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

def analyze_interactive(c_code, l_code):
    res = dbAPI.get_interactive_by_clcodes(c_code, l_code)
    if res == None or len(res) == 0:
        print("something went wrong")
    
    df = pd.DataFrame(res, columns=["user_uid", "worksheet_uid", "l_code", "c_code", "time"])
    df = df.drop(columns=["c_code", "l_code", "time"])
    
    groupby = df.groupby(by="user_uid")
    df2 = groupby.count().rename(columns={"worksheet_uid": "count"})
    df2 = df2[df2["count"]>1]
    
    d2 = pd.DataFrame("", index=df2.index, columns=["worksheets"])
    del df2
    
    for i, value in groupby.apply(aa, include_groups=False).items():
        if i in d2.index:
            d2.loc[i, "worksheets"] = value
    
    os.makedirs("./user_worksheets_indexes", exist_ok=True)
    d2.to_parquet(f"./user_worksheets_indexes/{c_code}-{l_code}.parquet")
    d2.to_csv(f"./user_worksheets_indexes/{c_code}-{l_code}.csv")
    
    df = df.groupby(by="worksheet_uid").apply(lambda group: ",".join(group["user_uid"]), include_groups=False)
    df.name = "users"
    df = pd.DataFrame(df)
    
    os.makedirs("./worksheet_users_indexes", exist_ok=True)
    df.to_parquet(f"./worksheet_users_indexes/{c_code}-{l_code}.parquet")
    df.to_csv(f"./worksheet_users_indexes/{c_code}-{l_code}.csv")
    
def aa(group):
    # print(group["worksheet_uid"])
    # print(group.values)
    return ",".join(group["worksheet_uid"])

def task(c_code, l_code):
    cos_df = calculate_cos_sim_by_country(c_code, l_code)
    n = 200
    top_n_df = top_n_cos_sim(cos_df, n)
    path = f"top_{n}_by_country_files"
    os.makedirs(path, exist_ok=True)
    top_n_df.to_parquet(f"{path}/top_{n}_{l_code}-{c_code}.parquet", index=False)
    cos_df.to_parquet(f'cos_sim_files/{l_code}-{c_code}.parquet', index=False)
    print(f"finished {l_code}-{c_code}")
    

analyze_interactive("IL", "he")
# try:
#     t = datetime.datetime.now()

#     with ThreadPoolExecutor(max_workers=10) as executor:
#         tasks = [executor.submit(task, c_code, l_code) for c_code, l_code in dbAPI.get_distinct_country_lang()]
#         for future in tasks:
#             future.result() # Wait for all tasks to complete
    
#     print(datetime.datetime.now()-t)
# except Exception as e:
#     print(e)
        
# finally:
sql_pool.close_conncections()