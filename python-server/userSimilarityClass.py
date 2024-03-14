import dbAPI
import pandas as pd
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity



def calculate_user_similarity(worksheet_uids, c_code, l_code):
    users = get_worksheets_users(worksheet_uids, c_code, l_code)
    
    worksheets, index = get_user_worksheets(users, c_code, l_code)
    
    Y = pd.get_dummies(worksheets).groupby(level=0).max()
    # Y = pd.DataFrame(0, index=worksheets.index.drop_duplicates(), columns=worksheets.drop_duplicates().values)
    # for i, row in worksheets.items():
    #     if i in Y.index:
    #         Y.loc[i, row] = 1
            
    X = pd.DataFrame(0, index=[1], columns=Y.columns)
    X.loc[1, worksheet_uids] = 1
    # X.to_csv("X.csv")
    # Y.to_csv("Y.csv")
    cos_sim = cosine_similarity(X.values, Y.values)
    cos_sim = pd.DataFrame(cos_sim, index=[1], columns=Y.index)
    return cos_sim, index

def top_n_sim_users(sim_one_row: pd.DataFrame, N, score_above=0.8):
    sim_one_row = sim_one_row.iloc[0].nlargest(N)
    sim_one_row = sim_one_row[sim_one_row>=score_above]
    return sim_one_row.index

def get_user_worksheets(users, c_code, l_code, **kwargs):
    path = f"./user_worksheets_indexes/{c_code}-{l_code}.parquet"
    worksheets_index = dbAPI.get_file_df(path) if kwargs.get("index", None) is None else kwargs.get("index")
    
    
    worksheets = worksheets_index.loc[(worksheets_index.index.isin(users)), "worksheets"]
    worksheets = worksheets.apply(lambda x: x.split(","))
    worksheets = worksheets.explode()
    
    return worksheets, worksheets_index

def get_worksheets_users(worksheet_uids, c_code, l_code):
    path = f"./worksheet_users_indexes/{c_code}-{l_code}.parquet"
    users_index = dbAPI.get_file_df(path)
    
    users = users_index.loc[worksheet_uids, "users"]
    users = users.apply(lambda x: x.split(","))
    users = users.explode().drop_duplicates()
    
    return users