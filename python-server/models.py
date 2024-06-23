import pandas as pd
import datetime
from analyticsOnExcel import interactive_user_similarity_analysis, markov, popular_in_month

from filter_manager import FilterFactory
import userSimilarityClass as uss
from functools import reduce


class MyModel:    
    def __init__(self, c_code, l_code) -> None:
        self.c_code = c_code
        self.l_code = l_code
        
    def predict(self, data, **kwargs):
        pass
    
    def fit(self, **kwargs):
        pass
    
class CosUserSimilarityModel(MyModel):
    def __init__(self, c_code, l_code) -> None:
        super().__init__(c_code, l_code)
        
    def predict(self, data, **kwargs):
        N = kwargs.get('n',20)
        popular = kwargs.get('popular', True)
        already_watched = kwargs.get('already_watched', [])
        if not isinstance(already_watched, list):
            raise Exception("already_watched is not a list")
        preds = self.recommend_users_alike(already_watched, data, self.c_code, self.l_code, n=N)
        if len(preds) >= N:
            return preds
        if popular:
            most_popular_model = MostPopularModel(self.c_code, self.l_code)
            diff = N-len(preds)
            filters = {
                'MonthFilter': {'months':[datetime.datetime.now().month]}
                }
            preds = preds + most_popular_model.predict(None, already_watched=preds, n=diff, filters=filters)
        
        return preds
    
    def fit(self, **kwargs):
        data, step_size = kwargs.get('data'), kwargs.get('step_size', 5)
        
        if 'data' not in kwargs:
            raise Exception('Needs data to fit to')
        
        interactive_user_similarity_analysis(data, step_size, self.c_code, self.l_code)
        
    def recommend_users_alike(self, already_watched, worksheet_uids, c_code, l_code, **kwargs):
        N = kwargs.get('n')
        score_above = 0.9
        (user_similarity, index)  = uss.calculate_user_similarity(worksheet_uids, c_code, l_code)
        
        while True:
            top_n_sim = uss.top_n_sim_users(user_similarity, score_above=score_above)
            users_worksheets, _ = uss.get_user_worksheets(top_n_sim, c_code, l_code, index=index)
            users_worksheets = users_worksheets.drop_duplicates()
            users_worksheets = users_worksheets[~users_worksheets.isin(already_watched+worksheet_uids)]
            
            if users_worksheets.size >= N or score_above < 0.3:
                if users_worksheets.size == 0:
                    return []
                break
            score_above -= 0.1
        # print("1")
        return users_worksheets.sample(min(users_worksheets.size, N)).to_list()
        
class CosPageSimilarityModel(MyModel):
    def __init__(self, c_code, l_code) -> None:
        super().__init__(c_code, l_code)
        
    def predict(self, data, **kwargs):
        pass
    
    def fit(self, **kwargs):
        pass
    
class MarkovModel(MyModel):
    def __init__(self, c_code, l_code) -> None:
        super().__init__(c_code, l_code)
    
    def predict(self, data, **kwargs):
        xs = [x[-1] for x in data]
        
        user_similarity_model = CosUserSimilarityModel(self.c_code, self.l_code)
        most_popular_model = MostPopularModel(self.c_code, self.l_code)
        N = kwargs.get('n', 10)
        df = pd.read_parquet(f"MarkovModelParquets/{self.c_code}-{self.l_code}.parquet")
        not_in_df = list(filter(lambda x: x not in df.index, xs))
        for uid in not_in_df:
            df.loc[uid,0] = []
        
        res = df.loc[xs].to_numpy().flatten()
        res = [list(r) for r in res]
        # print(res)
        for i, r in enumerate(res):
            if len(r)< N:
                diff = N-len(r)
                user_similarity_recommendations = user_similarity_model.predict(data[i],already_watched=r, n=diff, popular=False)
                res[i] = res[i] + user_similarity_recommendations
                # print(f"sim : {user_similarity_recommendations}")
                
                if len(res[i])< N:
                    diff = N-len(res[i])
                    filters = {
                        'MonthFilter': {'months':[datetime.datetime.now().month]}
                    }
                    mp_recommendations = most_popular_model.predict(None, already_watched=res[i], n=diff, filters=filters)
                    res[i] = res[i] + mp_recommendations
                    # print(mp_recommendations)
                    
                
        # print([len(r) for r in res])
        return [r[:min(N,len(r))] for r in res]
    
    def fit(self, **kwargs):
        # if 'data' not in kwargs or isinstance(kwargs.get('data'), pd.DataFrame):
        #     raise Exception('\'data\' is not in kwargs or not instance of pd.DataFrame')
        markov(kwargs.get('data'), self.c_code, self.l_code)
        
        
class MostPopularModel(MyModel):
    def __init__(self, c_code, l_code) -> None:
        super().__init__(c_code, l_code)
    
    def fit(self, **kwargs):
        popular_in_month(kwargs.get('data'), self.c_code, self.l_code)
    
    def predict(self, data, **kwargs):
        return self.most_popular_in_month(**kwargs)
    
    def most_popular_in_month(self, **kwargs):
        N = kwargs.get('n', 20)
        filter = FilterFactory.create_instance(**kwargs.get('filters', {}))
        if not self.c_code or not self.l_code:
            raise Exception('c_code and l_code must be send in json body')
        df = filter.run(pd.read_parquet(f'most_populars/{self.c_code}-{self.l_code}.parquet'))
        df = df.groupby(by='worksheet_uid', group_keys=False)[['count']].apply(lambda g: reduce(lambda acc, e: acc + e, g['count'], 0)).reset_index().sort_values(by=0, ascending=False)
        df = df[~df['worksheet_uid'].isin(kwargs.get('already_watched',[]))]
        df = df['worksheet_uid'].head(N)
        return list(df)