import numpy as np
import pandas as pd
from analyticsOnExcel import interactive_user_similarity_analysis, markov

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
        already_watched = kwargs.get('already_watched', [])
        if not isinstance(already_watched, list):
            raise Exception("already_watched is not a list")
        from service import recommend_users_alike
        return np.array([recommend_users_alike(already_watched, [i for i in t[t!=0]], self.c_code, self.l_code) for t in data], dtype=object)
    def fit(self, **kwargs):
        data, step_size = kwargs.get('data'), kwargs.get('step_size', 5)
        
        if 'data' not in kwargs:
            raise Exception('Needs data to fit to')
        
        interactive_user_similarity_analysis(data, step_size, self.c_code, self.l_code)
        
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
        N = kwargs.get('n', 10)
        df = pd.read_parquet(f"MarkovModelParquets/{self.c_code}-{self.l_code}.parquet")
        not_in_df = list(filter(lambda x: x not in df.index, data))
        for idx in not_in_df:
            df.loc[idx, 0] = []
        res = df.loc[data].to_numpy().flatten()
        return [r[:min(N,len(r))] for r in res]
    
    def fit(self, **kwargs):
        # if 'data' not in kwargs or isinstance(kwargs.get('data'), pd.DataFrame):
        #     raise Exception('\'data\' is not in kwargs or not instance of pd.DataFrame')
        markov(kwargs.get('data'), self.c_code, self.l_code)