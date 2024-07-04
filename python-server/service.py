from functools import reduce
import dbAPI
from pageclass import Worksheet
from analyzer import AnalyzerFactory
from wrapper import wrap
import numpy as np

from models import MarkovModel, MostPopularModel, CosUserSimilarityModel, MixedModel, CosPageSimilarityModel

def recommend(uids, n=20, c_code="IL", l_code="he"):
    model = CosPageSimilarityModel(c_code, l_code)
    preds = model.predict(uids)
    preds = preds[(np.argsort(preds, preds[:, 1])[::-1])]
    infos = get_worksheets_info(preds[:, 0], c_code, l_code)
    return [infos[uid] for uid in preds[:, 0]]

def recommend_users_alike(already_watched, worksheet_uids, c_code, l_code, **kwargs):
    model = CosUserSimilarityModel(c_code, l_code)
    preds = model.predict(worksheet_uids, already_watched=already_watched, n=kwargs.get('n',20))
    preds = preds[(np.argsort(preds, preds[:, 1])[::-1])]
    infos = get_worksheets_info(preds[:, 0], kwargs.get('cCode'), kwargs.get('lCode'))
    return [infos[uid] for uid in preds[:, 0]]

def update_files_recommendations(json):
    analyzers = AnalyzerFactory.create_instance(**json)
    wrapper = wrap(analyzers)
    wrapper.run()
    
def most_popular_in_month(**kwargs):
    model = MostPopularModel(kwargs.get('cCode'), kwargs.get('lCode'))
    preds = model.predict(None, **kwargs)
    preds = preds[(np.argsort(preds, preds[:, 1])[::-1])]
    infos = get_worksheets_info(preds[:, 0], kwargs.get('cCode'), kwargs.get('lCode'))
    return [infos[uid] for uid in preds[:, 0]]
    
    
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
    
def predict_markov(worksheet_uid, c_code, l_code, n, **kwargs):
    model = MarkovModel(c_code, l_code, n)
    
    preds = model.predict(worksheet_uid, n=n, grade=kwargs.get('grade'))
    preds = preds[(np.argsort(preds, preds[:, 1])[::-1])]
    infos = get_worksheets_info(preds[:, 0], kwargs.get('cCode'), kwargs.get('lCode'))
    return [infos[uid] for uid in preds[:, 0]]


def predict_mixed(uids, c_code, l_code, n, score_above, **kwargs):
    model = MixedModel(c_code, l_code, n)
    
    preds_df = model.predict(uids, n=n, grade=kwargs.get('grade'), score_above=score_above)
    if preds_df.empty:
        return []
    
    all_uids = list(preds_df.index)
    infos = get_worksheets_info(all_uids, c_code, l_code)
    
    return sorted(list(map(lambda x:  {**(infos[x[0]]), **(x[1])},preds_df.T.to_dict().items())), key=lambda x: x['score'], reverse=True)