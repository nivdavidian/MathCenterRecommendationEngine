import pandas as pd
import numpy as np
import datetime
import json
from analyticsOnExcel import interactive_user_similarity_analysis, markov, popular_in_month
from sklearn.metrics.pairwise import cosine_similarity

from filter_manager import FilterFactory
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
        """Predicts the next step of the user by the resemblence of his history against other users

        Args:
            data (List<String>): List of worksheet uids recommended the last 5
            already_watched: In kwargs can be sent as already watched pages will not return them if recommended by the algorithm

        Returns:
            np.ndarray: An array of pairs containing worksheet UIDs and their respective user scores as calculated by the algorithm.

        """
        # Read the User similarity parquet
        users = pd.read_parquet(f'UserSimilarityParquets/{self.l_code}.parquet', filters=[('0', 'in', data)])['user_uid'].unique()
        
        if len(users) == 0:
            return np.reshape(np.array([]), (-1,2))
        df = pd.read_parquet(f'UserSimilarityParquets/{self.l_code}.parquet', filters=[('user_uid', 'in', users)]).set_index('user_uid')
        
        Y = pd.get_dummies(df, prefix="", prefix_sep="").groupby(level=0).max()
        X = pd.DataFrame(0, index=[1], columns=Y.columns)
        
        if X.shape[1] == 0:
            return np.reshape(np.array([]), (-1,2))
        
        X.loc[1, Y.columns[Y.columns.isin(data)]] = 1
        
        cos_sim = cosine_similarity(X.values, Y.values)
        cos_sim = pd.DataFrame(cos_sim, index=[1], columns=Y.index)
        cos_sim = cos_sim.T.reset_index()
        
        df = df.reset_index()
        
        df = pd.merge(df, cos_sim, how='left', right_on='user_uid', left_on='user_uid').sort_values(by=[1, 'user_uid'], ascending=[False, False]).drop_duplicates(subset=['0', 1], keep='first')
        
        return df[['0', 1]].to_numpy()
    
    def fit(self, **kwargs):
        data, step_size = kwargs.get('data'), kwargs.get('step_size', 5)
        
        if 'data' not in kwargs:
            raise Exception('Needs data to fit to')
        
        interactive_user_similarity_analysis(data, step_size, self.c_code, self.l_code)
        
class CosPageSimilarityModel(MyModel):
    def __init__(self, c_code, l_code) -> None:
        super().__init__(c_code, l_code)
        
    def predict(self, data, **kwargs):
        # getting the parquet file of top recs by worksheet_uid as ordered by Page Similarity
        df = pd.read_parquet(f'top_by_country_files/{self.l_code}-{self.c_code}.parquet')
        df = json.loads(df.loc[data[-1], 'top_10'])
        df = np.reshape(np.array(df), (-1,2))
        return df
        
    def fit(self, **kwargs):
        pass
    
class MarkovModel(MyModel):
    def __init__(self, c_code, l_code, n) -> None:
        super().__init__(c_code, l_code)
        self.N = n
    
    def predict(self, data, **kwargs):
        # Last worksheet the user clicked
        last_page = data[-1]
        
        # Reading markov parquet that contains all markov results of the same %self.l_code
        df = pd.read_parquet(f"MarkovModelParquets/{self.l_code}.parquet")
        
        try:
            res = df.loc[last_page]
        except:
            return np.full((1,2), -1)
        
        res = np.reshape(res, (-1,2))
        
        s = res[:, 1].max()+1
        res[:, 1] = res[:, 1]/s
        return res
    
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
        """Generates list of most popular pages within the same language, picked grades and picked months.

        Args:
            data (None): Not relevant
            filters (Map): need to send filters of grades and months

        Returns:
            numpy.ndarray: return a ndarray with shape (n,2) returning pair of uid and count
        """
        return self.most_popular_in_month(**kwargs)
    
    def most_popular_in_month(self, **kwargs):
        N = kwargs.get('n', 20)
        filter = FilterFactory.create_instance(**kwargs.get('filters', {}))
        if not self.c_code or not self.l_code:
            raise Exception('c_code and l_code must be send in json body')
        df = filter.run(pd.read_parquet(f'most_populars/{self.c_code}-{self.l_code}.parquet'))
        df = df.groupby(by='worksheet_uid', group_keys=False)[['count']].apply(lambda g: reduce(lambda acc, e: acc + e, g['count'], 0)).reset_index().sort_values(by=0, ascending=False)
        df: np.ndarray = np.reshape(df[['worksheet_uid', 0]].head(N).to_numpy(), (-1,2))
        
        counts = df[:, 1].max() + 1
        
        df[:, 1] = df[:, 1]/counts
        
        # max_v = np.max(df[:, 1])
        # print(max_v)
        # print(df)
        
        # df[:, 1] = df[:, 1]/max_v
        return df
    
    
class MixedModel(MyModel):
    def __init__(self, c_code, l_code, n) -> None:
        super().__init__(c_code, l_code)
        self.N = n
    
    def fit(self, **kwargs):
        pass
    
    def predict(self, data, **kwargs):
        markov_per, us_per, mp_per, ps_per = 0.25, 0.25, 0.25, 0.25
        markov_model = MarkovModel(self.c_code, self.l_code, self.N)
        markov_res = markov_model.predict(data)
        
        us_model = CosUserSimilarityModel(self.c_code, self.l_code)
        us_res = us_model.predict(data, n=self.N)
        
        mp_model = MostPopularModel(self.c_code, self.l_code)
        filters = {
            'MonthFilter': {'months':list(range(1,13))}
            }
        if kwargs.get('grade'):
            filters['AgeFilter'] = {'ages': kwargs.get('grade')}
            
        mp_res = mp_model.predict(data, n=100, filters=filters)
        
        ps_model = CosPageSimilarityModel(self.c_code, self.l_code)
        ps_res = ps_model.predict(data)
        
        res = pd.DataFrame(0, index=(np.concatenate((markov_res[:, 0],us_res[:, 0],mp_res[:, 0], ps_res[:, 0]))), columns=['markov_score', 'us_score', 'mp_score', 'ps_score'], dtype='float64')
        res = res.reset_index(names='worksheet_uid').drop_duplicates().set_index('worksheet_uid')
        
        res.loc[markov_res[:, 0], 'markov_score'] = markov_res[:, 1].astype('float64')*markov_per
        res.loc[us_res[:, 0], 'us_score'] = us_res[:, 1].astype('float64')*us_per
        res.loc[mp_res[:, 0], 'mp_score'] = mp_res[:, 1].astype('float64')*mp_per
        res.loc[ps_res[:, 0], 'ps_score'] = ps_res[:, 1].astype('float64')*ps_per
        
        res['score'] = res.sum(axis=1)
        res = res.sort_values(by='score', ascending=False)
        
        res = res[res['score'] > kwargs.get('score_above',0)]
        res = res.head(kwargs.get('n', 10))
        
        # res.loc[markov_res[:, 0], 'markov_score'] = markov_res[:, 1].astype('float64')
        # res.loc[us_res[:, 0], 'us_score'] = us_res[:, 1].astype('float64')
        # res.loc[mp_res[:, 0], 'mp_score'] = mp_res[:, 1].astype('float64')
        # res.loc[ps_res[:, 0], 'ps_score'] = ps_res[:, 1].astype('float64')
        
        # return np.reshape(res.reset_index().to_numpy(), (-1,6))
        # print(list(res.index)[:20])
        
        return res
        
        
        