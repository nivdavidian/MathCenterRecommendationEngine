import dbAPI
import userSimilarityClass as uss
import pandas as pd
from filter_manager import FilterFactory
from pageclass import Worksheet
from analyzer import AnalyzerFactory
from wrapper import wrap
from functools import reduce

def recommend(worksheet_uid, n=20, c_code="IL", l_code="he"):
    worksheet = Worksheet(worksheet_uid=worksheet_uid, c_code=c_code, l_code=l_code)
    worksheet.build_page()
    rec = worksheet.get_rec(n)
    return rec

def recommend_users_alike(already_watched, worksheet_uids, c_code, l_code):
    N = 20
    score_above = 1
    (user_similarity, index)  = uss.calculate_user_similarity(worksheet_uids, c_code, l_code)
    
    while True:
        top_n_sim = uss.top_n_sim_users(user_similarity, score_above=score_above)
        users_worksheets, _ = uss.get_user_worksheets(top_n_sim, c_code, l_code, index=index)
        users_worksheets = users_worksheets.drop_duplicates()
        users_worksheets = users_worksheets[~users_worksheets.isin(already_watched+worksheet_uids)]
        
        if users_worksheets.size >= N or score_above < 0.3:
            # print(len(users_worksheets), score_above)
            # return popular or alike the last page
            if users_worksheets.size == 0:
                users_worksheets = pd.Series(["-1"])
            break
        score_above -= 0.05
    # print("1")
    return users_worksheets.sample(min(users_worksheets.size, N)).to_list()

def update_files_recommendations(json):
    analyzers = AnalyzerFactory.create_instance(**json)
    wrapper = wrap(analyzers)
    wrapper.run()
    
def most_popular_in_month(**kwargs):
    filter = FilterFactory.create_instance(**kwargs.get('filters', {}))
    c_code, l_code = kwargs.get('cCode', None), kwargs.get('lCode', None)
    if not c_code or not l_code:
        raise Exception('c_code and l_code must be send in json body')
    
    df = filter.run(pd.read_parquet(f'most_populars/{c_code}-{l_code}.parquet'))
    df = df.groupby(by='worksheet_uid', group_keys=False).apply(lambda g: reduce(lambda acc, e: acc + e, g['count'], 0)).reset_index().sort_values(by=0, ascending=False)
    df = df['worksheet_uid'].head(10)
    res_info = get_worksheets_info(df.to_list(), c_code, l_code)
    res_info = [res_info[uid] for uid in df]
    return res_info
    
def get_worksheets_info(uids, c_code, l_code):
    infos = dbAPI.get_worksheet_info(uids, c_code, l_code)
    m = {}
    for row in infos:
        uid, topic , min_grade, max_grade, title = row
        if uid in m:
            m[uid]['topics'].append(topic)
        else:
            m[uid] = {'uid': uid, 'topics': [topic], 'min_grade': min_grade, 'max_grade': max_grade, 'name': title}
        
    return m
    
        