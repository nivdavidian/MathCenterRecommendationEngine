import pandas as pd
import json
import datetime
import dbAPI
import numpy as np
import os
import sql_pool

from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor


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

def calculate_cos_sim_by_country(c_code, l_code):
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
    
    df2 = pd.DataFrame(dbAPI.get_worksheet_grades_by_country_lang(c_code, l_code), columns = ["worksheet_uid", "country_code", "language_code"])
    
    df2 = pd.merge(df2, df3, on=["worksheet_uid", "country_code", "language_code"], how='left')
    del df3
    
    uniq_pages = df2["worksheet_uid"].unique()
    
    df = pd.DataFrame(dbAPI.get_all_pages_topics(), columns=["worksheet_uid", "topic"])

    uniq_topics = df["topic"].unique()
    
    zeroes_df = pd.DataFrame(0, index=uniq_pages, columns=np.concatenate((uniq_topics, np.array(range(1,13)))))

    for _, row in df.iterrows():
        if row["worksheet_uid"] in zeroes_df.index:
            zeroes_df.loc[row["worksheet_uid"], row["topic"]] = 1
    del df
    
    for _, row in df2.iterrows():
        if pd.isna(row["month"]):
            continue
        zeroes_df.loc[row["worksheet_uid"], row["month"]] = 1
    del df2
    
    cos_sim = cosine_similarity(zeroes_df.values)

    cos_sim_df = pd.DataFrame(cos_sim, index=zeroes_df.index, columns=zeroes_df.index)
    del zeroes_df
    
    return cos_sim_df

def top_n_cos_sim(df, n):

    top_10_df = pd.DataFrame({"worksheet_uid": df.index},index=df.index)
    top_10_df["top_10"] = ''

    for index, row in df.iterrows(): 
        top_10_df.loc[index, "top_10"] = ','.join(row.sort_values(ascending=False).head(n).index.to_list())

    return top_10_df

def task(c_code, l_code):
    cos_df = calculate_cos_sim_by_country(c_code, l_code)
    n = 10
    top_n_df = top_n_cos_sim(cos_df, n)
    path = f"top_{n}_by_country_files"
    os.makedirs(path, exist_ok=True)
    top_n_df.to_csv(f"{path}/top_{n}_{l_code}-{c_code}.csv", index=False)
    cos_df.to_csv(f'cos_sim_files/{l_code}-{c_code}.csv', index=False)
    print(f"finished {l_code}-{c_code}")
    

# task("AE", "ar")
try:
    t = datetime.datetime.now()

    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = [executor.submit(task, c_code, l_code) for c_code, l_code in dbAPI.get_distinct_country_lang()]
        for future in tasks:
            future.result() # Wait for all tasks to complete
    
    print(datetime.datetime.now()-t)
except Exception as e:
    print(e)
        
finally:
    
    sql_pool.close_conncections()