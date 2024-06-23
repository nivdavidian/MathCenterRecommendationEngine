import dbAPI
import pandas as pd
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity



def calculate_user_similarity(worksheet_uids, c_code, l_code):
    users = get_worksheets_users(worksheet_uids, c_code, l_code)
    
    worksheets, index = get_user_worksheets(users, c_code, l_code, col="original_uid")
    del users
    
    Y = pd.get_dummies(worksheets).groupby(level=0).max()
            
    X = pd.DataFrame(0, index=[1], columns=Y.columns)
    
    # print(worksheet_uids)
    if X.shape[1] == 0:
        return pd.DataFrame([[0]]), index
    X.loc[1, Y.columns[Y.columns.isin(worksheet_uids)]] = 1
    cos_sim = cosine_similarity(X.values, Y.values)
    cos_sim = pd.DataFrame(cos_sim, index=[1], columns=Y.index)
    return cos_sim, index

def top_n_sim_users(sim_one_row: pd.DataFrame, score_above=0.8):
    sim_one_row = sim_one_row.iloc[0][sim_one_row.iloc[0]>=score_above]
    # print(sim_one_row)
    sim_one_row.sort_values()
    return sim_one_row.index

def get_user_worksheets(users, c_code, l_code, **kwargs):
    path = f"./user_worksheets_indexes/{c_code}-{l_code}.parquet"
    worksheets_index = dbAPI.get_file_df(path) if kwargs.get("index", None) is None else kwargs.get("index")
    
    worksheets_index = worksheets_index.set_index(kwargs.get("col", "user_uid"))
    # print(worksheets_index.index)
    # print(users)
    users = list(filter(lambda x: x in worksheets_index.index, users))
    # print(users)
    # print(users)
    worksheets = worksheets_index.loc[users]
    worksheets = worksheets.explode('worksheets').reset_index(drop=False)
    worksheets = pd.Series(data=worksheets['worksheets'].values, index=worksheets['user_uid'].values)
    # print(worksheets.head(5))
    worksheets.index.name = 'user_uid'
    
    return worksheets, worksheets_index

def get_worksheets_users(worksheet_uids, c_code, l_code):
    path = f"./worksheet_users_indexes/{c_code}-{l_code}.parquet"
    users_index = dbAPI.get_file_df(path)
    
    users = users_index.loc[users_index.index[users_index.index.isin(worksheet_uids)], "users"]
    users = users.apply(lambda x: x.split(","))
    users = users.explode().drop_duplicates()
    
    return users