import pandas as pd
import json
import dbAPI
import numpy as np
import os

from enum import Enum
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD

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
    """
    Analyze and process user download data.

    This function retrieves all user download data from the database, processes it to extract and 
    structure relevant information, and returns a cleaned DataFrame with unique download records.

    Steps performed:
    1. Retrieve user download data from the database.
    2. Parse the downloads column to extract individual download records.
    3. Explode the downloads column to create a row for each download record.
    4. Extract worksheet UID and download timestamp from each record.
    5. Remove duplicate rows based on user UID and worksheet UID.
    6. Extract year, month, and day from the download timestamp.
    7. Drop unnecessary columns and return a DataFrame with unique download records.

    Returns:
    DataFrame: A cleaned DataFrame containing unique download records with columns for country code,
               language code, worksheet UID, and month of download.
    """
    
    # Step 1: Retrieve user download data from the database
    res = dbAPI.get_all_user_downloads()
    
    # Step 2: Create a DataFrame with the retrieved data
    df3 = pd.DataFrame(res, columns=["user_uid", "country_code", "language_code", "downloads"])
    
    # Step 3: Parse the downloads column to extract individual download records
    df3["downloads"] = df3["downloads"].apply(lambda x: list(json.loads(x[1:-1])))
    
    # Step 4: Explode the downloads column to create a row for each download record
    df3 = df3.explode("downloads").reset_index(drop=True)
    
    # Step 5: Extract worksheet UID and download timestamp from each record
    df3["worksheet_uid"] = df3["downloads"].apply(lambda x: x["pageUid"])
    df3["downloads"] = pd.to_datetime(df3["downloads"].apply(lambda x: x["time"]), utc=True)
    
    # Step 6: Remove duplicate rows based on user UID and worksheet UID
    rows_to_remove = []
    for index, row in df3.iterrows():
        if index + 1 < len(df3):
            next_row = df3.iloc[index + 1]
            if row['user_uid'] == next_row['user_uid'] and row['worksheet_uid'] == next_row['worksheet_uid']:
                rows_to_remove.append(index)
    
    df3 = df3.drop(rows_to_remove).reset_index(drop=True)
    
    # Step 7: Extract year, month, and day from the download timestamp
    df3["year"] = df3["downloads"].dt.year
    df3["month"] = df3["downloads"].dt.month
    df3["day"] = df3["downloads"].dt.day
    
    # Step 8: Drop unnecessary columns
    df3 = df3.drop(columns=['downloads', 'user_uid', 'day', 'year'])
    
    # Step 9: Retain only relevant columns and remove duplicate rows
    df3 = df3[["country_code", "language_code", "worksheet_uid", "month"]]
    df3 = df3.drop_duplicates()
    
    return df3

def calculate_cos_sim_by_country(c_code, l_code):
    """
    Calculate the cosine similarity of worksheets by country and language.

    This function retrieves worksheet data based on country and language codes, processes the data to
    create a feature matrix including topics and grades, and calculates the cosine similarity between
    the worksheets.

    Parameters:
    c_code (str): The country code.
    l_code (str): The language code.

    Returns:
    DataFrame: A DataFrame containing the cosine similarity scores between worksheets, where the index and columns
               are worksheet UIDs.
    """
    
    # Step 1: Retrieve worksheet grades data by country and language
    df2 = pd.DataFrame(dbAPI.get_worksheet_grades_by_country_lang(c_code, l_code), 
                       columns=["worksheet_uid", "min_grade", "max_grade"])
    
    # Step 2: Retrieve all pages topics
    df = pd.DataFrame(dbAPI.get_all_pages_topics(), columns=["worksheet_uid", "topic"])
    
    # Step 3: Create a one-hot encoded matrix of topics
    df = pd.get_dummies(df, columns=['topic'], prefix="", prefix_sep="").groupby(by='worksheet_uid').any()
    
    # Step 4: Merge the grades data with the topics data
    df = pd.merge(df2, df, on='worksheet_uid', how='left')
    
    # Step 5: Generate grade names for each worksheet based on min and max grade values
    df['grades'] = df.apply(lambda x: EnumManipulation.enum_names_by_value(
        list(range(EnumManipulation.convert_to_enum_value(x['min_grade']), 
                   EnumManipulation.convert_to_enum_value(x['max_grade']) + 1))), axis=1)
    
    # Step 6: Drop the original grade columns and explode the grades column
    df = df.drop(columns=['min_grade', 'max_grade']).explode('grades')
    
    # Step 7: Create a one-hot encoded matrix of grades and combine with the topics data
    df = pd.get_dummies(df, columns=['grades'], prefix="", prefix_sep="").groupby(level=0).max()
    
    # Step 8: Set the worksheet UID as the index
    df = df.set_index('worksheet_uid')
    
    # Apply SVD
    n_components = 10  # Adjust based on your requirements
    svd = TruncatedSVD(n_components=n_components)
    reduced_data = svd.fit_transform(df.values)
    
    # Step 9: Calculate the cosine similarity between the worksheets
    cos_sim = cosine_similarity(reduced_data)
    
    # Step 10: Create a DataFrame for the cosine similarity scores
    cos_sim_df = pd.DataFrame(cos_sim, index=df.index, columns=df.index)
    
    return cos_sim_df

def top_n_cos_sim(df: pd.DataFrame, n):
    """
    Identify the top N cosine similarity scores for each worksheet.

    This function processes a DataFrame of cosine similarity scores, identifying the top N
    highest similarity scores (above a threshold of 0.4) for each worksheet. It excludes self-similarity
    (the diagonal elements) and returns a DataFrame where each row contains the top N similarities
    for the corresponding worksheet in JSON format.

    Parameters:
    df (pd.DataFrame): A DataFrame containing cosine similarity scores between worksheets.
    n (int): The number of top similarities to return for each worksheet.

    Returns:
    pd.DataFrame: A DataFrame with a single column 'top_n' containing the top N cosine similarity scores
                  for each worksheet in JSON format.
    """
    
    # Apply a lambda function to each row of the DataFrame
    df = df.apply(
        lambda row: json.dumps(
            list(
                # Select similarity scores excluding self-similarity and those below 0.4
                row.loc[(row.index != row.name) & (row >= 0.5)]
                # Sort the similarity scores in descending order
                .sort_values(ascending=False)
                # .head(100)
                # Convert the selected scores to a list of tuples
                .items()
            )
        ),
        axis=1
    )
    
    # Rename the series to 'top_10'
    df.name = 'top_10'
    
    # Convert the series to a DataFrame
    df = df.to_frame()
    
    return df

def interactive_user_similarity_analysis(data: pd.DataFrame, step, c_code, l_code):
    """
    Perform interactive user similarity analysis and save the results to a Parquet file.

    This function processes user interaction data to prepare it for user similarity analysis.
    It filters and transforms the data, segments user histories into chunks, and saves the processed
    data to a Parquet file for further analysis.

    Parameters:
    data (pd.DataFrame): The input DataFrame containing user interaction data with columns ['user_uid', 'worksheet_uid', 'time'].
    step (int): The step size used to segment user histories.
    c_code (str): The country code.
    l_code (str): The language code.

    Returns:
    None
    """
    
    # Drop duplicate rows and reset the index
    data = data.drop_duplicates().reset_index(drop=True)
    
    # Convert the 'time' column to datetime format
    data["time"] = pd.to_datetime(data["time"], format="%Y-%m-%d %H:%M:%S")
    
    # Sort the data by 'user_uid' in descending order and 'time' in ascending order
    data = data.sort_values(by=['user_uid', 'time'], ascending=[False, True])
    
    # Extract date information to the nearest hour and drop duplicates within the same hour for each user and worksheet
    data['date'] = data["time"].dt.strftime('%Y-%m-%d %H')
    data = data.drop_duplicates(subset=['user_uid', 'worksheet_uid', 'date'], keep='first')[['user_uid', 'worksheet_uid', 'time']]
    
    # Group by 'user_uid' and filter out users with only one interaction
    df2 = data.groupby(by='user_uid', sort=False, group_keys=False).count()
    df2 = df2[df2['worksheet_uid'] > 1]
    data = data[data['user_uid'].isin(df2.index)].reset_index(drop=True)
    
    # Segment user histories into chunks based on the step size
    n = step * 2
    data = data.groupby(by='user_uid')[['worksheet_uid']].apply(
        lambda g: ([list(g['worksheet_uid'])] + 
                   [g['worksheet_uid'].to_list()[i*step:min(len(g['worksheet_uid'].to_list()), i*step+n)] 
                    for i in range(int(len(g["worksheet_uid"].to_list())/step) 
                                   if len(g["worksheet_uid"].to_list()) > n else 0)])
    )
    
    # Explode the list of segments into separate rows
    data = data.explode().reset_index()
    
    # Modify 'user_uid' to include a unique prefix
    data['user_uid'] = [f"{i}_" for i in data.index] + data['user_uid']
    
    # Explode the segments to create separate rows for each worksheet_uid
    data = data.explode(0)
    
    # Ensure the directory for saving Parquet files exists
    os.makedirs("./UserSimilarityParquets", exist_ok=True)
    
    # Save the processed data to a Parquet file
    data.to_parquet(f'UserSimilarityParquets/{l_code}.parquet', index=False)
    
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
    
def markov(df: pd.DataFrame, c_code, l_code):
    """
    Perform a Markov model analysis on user interaction data and save the results to a Parquet file.

    This function processes user interaction data to create a transition matrix based on user interactions
    with worksheets. It filters, transforms, and groups the data to identify transitions between worksheets
    within a 30-day period, and saves the resulting transition counts to a Parquet file.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing user interaction data with columns ['user_uid', 'worksheet_uid', 'time', 'c_code', 'l_code'].
    c_code (str): The country code.
    l_code (str): The language code.

    Returns:
    None
    """
    
    # Step 1: Drop duplicate rows and reset the index
    df = df.drop_duplicates().reset_index(drop=True)
    
    # Step 2: Convert the 'time' column to datetime format
    df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
    
    # Step 3: Sort the data by 'user_uid' and 'time'
    df = df.sort_values(by=['user_uid', 'time'], ascending=[True, True])
    
    # Step 4: Identify users with multiple interactions
    df['count'] = 0
    df2 = df.groupby(by=['user_uid'], group_keys=False)[['count']].count().reset_index()
    df2 = df2[df2['count'] > 1]
    
    # Step 5: Filter data to include only users with multiple interactions
    df = df[df['user_uid'].isin(df2['user_uid'])]
    
    # Step 6: Drop unnecessary columns
    df = df.drop(columns=['count', 'c_code', 'l_code'])
    
    # Step 7: Create shifted DataFrame to identify transitions
    df = pd.concat([df, df.shift(-1).rename(columns={"user_uid": "user_uid_1", "worksheet_uid": "worksheet_uid_1", "time": "time_1"})], axis=1)
    
    # Step 8: Filter transitions within a 30-day period
    df = df[(df["user_uid"] == df["user_uid_1"]) & 
            (df["worksheet_uid"] != df["worksheet_uid_1"]) & 
            (df["time_1"] - df["time"] < pd.Timedelta(days=30))].reset_index(drop=True)
    
    # Step 9: Drop unnecessary columns after filtering
    df = df.drop(['user_uid_1', 'user_uid', 'time'], axis=1)
    
    # Step 10: Group by worksheet transitions and count occurrences
    df = df.groupby(by=['worksheet_uid', 'worksheet_uid_1'], group_keys=False).count().rename(columns={'time_1': 'count'}).reset_index()
    
    # Step 11: Sort by 'worksheet_uid' and 'count'
    df = df.sort_values(by=['worksheet_uid', 'count'], ascending=[False, False]).set_index('worksheet_uid')
    
    # Step 12: Ensure the directory for saving Parquet files exists
    os.makedirs('MarkovModelParquets', exist_ok=True)
    
    # Step 13: Save the processed data to a Parquet file
    df.to_parquet(f"MarkovModelParquets/{l_code}.parquet")
    
def popular_in_month(df, c_code, l_code):
    """
    Analyze the popularity of worksheets by month and save the results to a Parquet file.

    This function processes user interaction data to calculate the popularity of worksheets for each month.
    It filters, transforms, and groups the data to identify the most popular worksheets by month, and
    saves the resulting popularity counts and grade information to a Parquet file.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing user interaction data with columns ['user_uid', 'worksheet_uid', 'time', 'c_code', 'l_code'].
    c_code (str): The country code.
    l_code (str): The language code.

    Returns:
    None
    """
    
    # Step 1: Drop duplicate rows and reset the index
    df = df.drop_duplicates().reset_index(drop=True)
    
    # Step 2: Extract the month from the 'time' column
    df["month"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S").apply(lambda x: x.month)
    
    # Step 3: Drop unnecessary columns
    df = df.drop(columns=["c_code", "l_code", "user_uid", "time"])
    
    # Step 4: Add a temporary 'count' column for counting interactions
    df['count'] = 0
    
    # Step 5: Group by 'worksheet_uid' and 'month' and count occurrences
    df = df.groupby(by=['worksheet_uid', 'month'], sort=False).count().reset_index().sort_values(by=['month', 'count'], ascending=[True, False])
    
    # Step 6: Retrieve grade information for the worksheets
    df2 = pd.DataFrame(dbAPI.get_worksheet_grades_by_uids(df['worksheet_uid'].unique(), c_code, l_code), columns=['worksheet_uid', 'min_grade', 'max_grade'])
    
    # Step 7: Merge the grade information with the main DataFrame
    df = pd.merge(df, df2, on='worksheet_uid')
    
    # Step 8: Generate grade names for each worksheet based on min and max grade values
    df['grades'] = df.apply(lambda x: EnumManipulation.enum_names_by_value(
        list(range(EnumManipulation.convert_to_enum_value(x['min_grade']), 
                   EnumManipulation.convert_to_enum_value(x['max_grade']) + 1))), axis=1)
    
    # Step 9: Drop the original grade columns and explode the grades column
    df = df.drop(columns=['min_grade', 'max_grade']).explode('grades')
    
    # Step 10: Create a one-hot encoded matrix of grades and combine with the main DataFrame
    df = pd.get_dummies(df, columns=['grades'], prefix="", prefix_sep="").groupby(level=0).max()
    
    # Step 11: Ensure the directory for saving Parquet files exists
    os.makedirs('most_populars', exist_ok=True)
    
    # Step 12: Save the processed data to a Parquet file
    df.to_parquet(f"most_populars/{c_code}-{l_code}.parquet")

def task(c_code, l_code, n):
    """
    Calculate and save the top N cosine similarity scores for worksheets by country and language.

    This function calculates the cosine similarity of worksheets for a given country and language,
    identifies the top N highest similarity scores for each worksheet, and saves the results to a Parquet file.

    Parameters:
    c_code (str): The country code.
    l_code (str): The language code.
    n (int): The number of top similarities to return for each worksheet.

    Returns:
    None
    """
    
    # Step 1: Calculate the cosine similarity matrix for worksheets by country and language
    cos_df = calculate_cos_sim_by_country(c_code, l_code)
    
    # Step 2: Identify the top N cosine similarity scores for each worksheet
    top_n_df = top_n_cos_sim(cos_df, n)
    
    # Step 3: Ensure the directory for saving the Parquet files exists
    path = "top_by_country_files"
    os.makedirs(path, exist_ok=True)
    
    # Step 4: Save the top N similarity scores to a Parquet file
    top_n_df.to_parquet(f"{path}/{l_code}-{c_code}.parquet", index=True)