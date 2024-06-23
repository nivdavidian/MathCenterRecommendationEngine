import dbAPI
from pageclass import Worksheet
from analyzer import AnalyzerFactory
from wrapper import wrap

from models import MarkovModel, MostPopularModel, CosUserSimilarityModel

def recommend(worksheet_uid, n=20, c_code="IL", l_code="he"):
    worksheet = Worksheet(worksheet_uid=worksheet_uid, c_code=c_code, l_code=l_code)
    # worksheet.build_page()
    rec = worksheet.get_rec(n)
    return rec

def recommend_users_alike(already_watched, worksheet_uids, c_code, l_code, **kwargs):
    model = CosUserSimilarityModel(c_code, l_code)
    return model.predict(worksheet_uids, already_watched=already_watched, n=kwargs.get('n',20))

def update_files_recommendations(json):
    analyzers = AnalyzerFactory.create_instance(**json)
    wrapper = wrap(analyzers)
    wrapper.run()
    
def most_popular_in_month(**kwargs):
    model = MostPopularModel(kwargs.get('cCode'), kwargs.get('lCode'))
    return model.predict(None, **kwargs)
    
    
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
    
def predict_markov(worksheet_uid, c_code, l_code, n):
    model = MarkovModel(c_code, l_code)
    preds = model.predict([[worksheet_uid]], n=n)
    preds = list(preds[0])
    if len(preds) == 0:
        return []
    infos = get_worksheets_info(preds, c_code, l_code)
    return [infos[uid] for uid in preds]