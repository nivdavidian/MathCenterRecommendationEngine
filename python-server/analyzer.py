from factory import AbstractFactory
from abc import ABC, abstractmethod
from analyticsOnExcel import task
from wrapper import Wrapper
from models import MarkovModel, MostPopularModel, CosUserSimilarityModel
import dbAPI
import pandas as pd



class Analyzer(ABC, Wrapper):
    
    
    def __init__(self) -> None:
        super().__init__()
        
    @abstractmethod
    def analyze(self):
        pass
    
class PagesSimilarityAnalyzer(Analyzer):
    
    def __init__(self, **kwargs):
        super().__init__()
        self.c_code = kwargs.get('c_code')
        self.l_code = kwargs.get('l_code')
        self.n = kwargs.get('n')
    
    def analyze(self):
        task(self.c_code, self.l_code, self.n)
        from recServer import logger
        logger.info(f'Finished update recommendatiom of Page Similarity in {self.c_code}-{self.l_code}')
    
    def run(self):
        super().run(self.analyze)
        
    
class UsersSimilarityAnalyzer(Analyzer):
    
    def __init__(self, **kwargs):
        super().__init__()
        self.model = CosUserSimilarityModel(kwargs.get('c_code'), kwargs.get('l_code'))
        self.step_size = kwargs.get('step_size', 5)
        
    
    def analyze(self):
        data = pd.DataFrame(dbAPI.get_interactive_by_clcodes(self.model.c_code,self.model.l_code), columns=['user_uid', 'worksheet_uid', 'l_code', 'c_code', 'time'])
        self.model.fit(data=data, step_size=self.step_size)
        from recServer import logger
        logger.info(f'Finished update recommendation of User Similarity in {self.model.l_code}')
    def run(self):
        super().run(self.analyze)
        
class MostPopular(Analyzer):
    def __init__(self, **kwargs):
        super().__init__()
        self.model = MostPopularModel(kwargs.get('c_code'), kwargs.get('l_code'))
    def analyze(self):
        self.model.fit(data=pd.DataFrame(dbAPI.get_interactive_by_clcodes(self.model.c_code, self.model.l_code), columns=["user_uid", "worksheet_uid", "l_code", "c_code", "time"]))
        from recServer import logger
        logger.info(f'Finished update recommendation of Most Popular in {self.model.c_code}-{self.model.l_code}')
    def run(self):
        super().run(self.analyze)

class MarkovAnalyzer(Analyzer):
    def __init__(self, **kwargs):
        super().__init__()
        self.model = MarkovModel(kwargs.get('c_code'),kwargs.get('l_code'), kwargs.get('n', 20))
    def analyze(self):
        self.model.fit(data=pd.DataFrame(dbAPI.get_interactive_by_clcodes(self.model.c_code, self.model.l_code), columns=['user_uid', 'worksheet_uid', 'c_code', 'l_code', 'time']))
        from recServer import logger
        logger.info(f'Finished update recommendation of Markov Model in {self.model.l_code}')
    def run(self):
        super().run(self.analyze)
    

class AnalyzerFactory(AbstractFactory):
    
    @classmethod
    def create_instance(cls, **kwargs):
        options = {
            'cl_codes': 'all', 
            'n': 200,
            'step_size': 5
        }
        
        if 'analyzers' not in kwargs or len(kwargs.get('analyzers')) == 0:
            raise('\'analyzers\' missing')
        
        cl_codes = list(set(map(lambda x: x[1], dbAPI.get_distinct_cl_codes())))
        options.update(kwargs.get('global_options', {}))
        
        analyzers = []
        for name, info in kwargs.get('analyzers').items():
            options_copy = options.copy()
            options_copy.update(info.get('options', {}))
            if options_copy.get('cl_codes') == 'all':
                options_copy['cl_codes'] = cl_codes
            if not isinstance(options_copy['cl_codes'], list):
                raise Exception("cl_codes must be an array")
            # if len(list(filter(lambda x: x not in cl_codes, options_copy['cl_codes']))) > 0:
            #     raise Exception("some cl_codes are invalid")
            if name == "PagesSimilarity":
                analyzers.extend([PagesSimilarityAnalyzer(c_code=cl_code[0], l_code=cl_code[1], n=options_copy['n']) for cl_code in list(map(lambda x: list(x), dbAPI.get_distinct_cl_codes()))])
            elif name == "UserSimilarity":
                step_size = int(options_copy.get("step_size"))
                analyzers.extend([UsersSimilarityAnalyzer(step_size=step_size, c_code=None, l_code=cl_code) for cl_code in options_copy['cl_codes']])
            elif name == "MostPopular":
                analyzers.extend([MostPopular(c_code=cl_code[0], l_code=cl_code[1]) for cl_code in list(map(lambda x: list(x), dbAPI.get_distinct_cl_codes()))])
            elif name == "MarkovModel":
                analyzers.extend([MarkovAnalyzer(c_code=None, l_code=cl_code) for cl_code in options_copy['cl_codes']])
            else:
                raise Exception(f"Analyzing job named, {name} does not exist")
        
        return analyzers
            
            
            
        
        
        
        
            
