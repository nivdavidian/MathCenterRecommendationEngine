import userSimilarityClass as uss
import pandas as pd
from filter_manager import FilterFactory
from pageclass import Worksheet
from analyzer import AnalyzerFactory
from wrapper import wrap




def recommend(worksheet_uid, n=20, c_code="IL", l_code="he"):
    worksheet = Worksheet(worksheet_uid=worksheet_uid, c_code=c_code, l_code=l_code)
    worksheet.build_page()
    rec = worksheet.get_rec(n)
    return rec

def recommend_users_alike(already_watched, worksheet_uids, c_code, l_code):
    N = 10
    score_above = 0.8
    (user_similarity, index)  = uss.calculate_user_similarity(worksheet_uids, c_code, l_code)
    
    while True:
        top_n_sim = uss.top_n_sim_users(user_similarity, score_above=score_above)
        users_worksheets, _ = uss.get_user_worksheets(top_n_sim, c_code, l_code, index=index)
        users_worksheets = users_worksheets.drop_duplicates()
        users_worksheets = users_worksheets[~users_worksheets.isin(already_watched+worksheet_uids)]
        
        if users_worksheets.size >= N or score_above <= 0.3:
            # print(len(users_worksheets), score_above)
            # return popular or alike the last page
            break
        score_above -= 0.15
    # print("1")
    return users_worksheets.sample(min(users_worksheets.size, N)).to_list()

def update_files_recommendations(json):
    analyzers = AnalyzerFactory.create_instance(**json)
    wrapper = wrap(analyzers)
    wrapper.run()
    
def most_popular_in_month(**kwargs):
    filter = FilterFactory.create_instance(**kwargs.get('filters', {}))
    df = filter.run(pd.read_parquet('111.parquet')).sort_values(by='count', ascending=False).reset_index(drop=True)
    df = df['worksheet_uid'].head(10)
    return df.tolist()
    
    
    
        