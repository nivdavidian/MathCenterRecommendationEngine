import userSimilarityClass as uss
import random
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
        top_n_sim = uss.top_n_sim_users(user_similarity, N, score_above=score_above)
        users_worksheets, _ = uss.get_user_worksheets(top_n_sim, c_code, l_code, index=index)
        users_worksheets = users_worksheets.drop_duplicates()
        users_worksheets = list(filter(lambda x: x not in worksheet_uids and x not in already_watched, users_worksheets))
        
        if len(users_worksheets) >= N or score_above <= 0.3:
            # return popular or alike the last page
            break
        score_above -= 0.05
    
    return random.sample(users_worksheets, (min(len(users_worksheets), N)))

def update_files_recommendations(json):
    analyzers = AnalyzerFactory.create_instance(**json)
    wrapper = wrap(analyzers)
    wrapper.run()
    
    
        