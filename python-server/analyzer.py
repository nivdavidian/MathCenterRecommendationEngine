from factory import AbstractFactory
from abc import ABC, abstractmethod
from analyticsOnExcel import interactive_user_similarity_analysis, task, popular_in_month
from wrapper import Wrapper
from models import MarkovModel, MostPopularModel
import dbAPI



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
    
    def run(self):
        super().run(self.analyze)
        
    
class UsersSimilarityAnalyzer(Analyzer):
    
    def __init__(self, **kwargs):
        super().__init__()
        self.data = kwargs.get('data')
        self.step_size = kwargs.get('step_size')
        self.c_code = kwargs.get('c_code')
        self.l_code = kwargs.get('l_code')
        
    
    def analyze(self):
        interactive_user_similarity_analysis(self.data, self.step_size, self.c_code, self.l_code)
    def run(self):
        super().run(self.analyze)
        
class MostPopular(Analyzer):
    def __init__(self, **kwargs):
        super().__init__()
        self.model = MostPopularModel(kwargs.get('c_code'), kwargs.get('l_code'))
    def analyze(self):
        import pandas as pd
        self.model.fit(data=pd.DataFrame(dbAPI.get_interactive_by_clcodes(self.model.c_code, self.model.l_code), columns=["user_uid", "worksheet_uid", "l_code", "c_code", "time"]))
    def run(self):
        super().run(self.analyze)

class MarkovAnalyzer(Analyzer):
    def __init__(self, **kwargs):
        super().__init__()
        self.model = MarkovModel(kwargs.get('c_code'),kwargs.get('l_code'))
    def analyze(self):
        import pandas as pd
        self.model.fit(data=pd.DataFrame(dbAPI.get_interactive_by_clcodes(self.model.c_code, self.model.l_code), columns=['user_uid', 'worksheet_uid', 'c_code', 'l_code', 'time']))
    def run(self):
        super().run(self.analyze)
    

class AnalyzerFactory(AbstractFactory):
    
    @classmethod
    def create_instance(cls, **kwargs):
        options = {
            'cl_codes': 'all', 
            'n': 50,
            'step_size': 10
        }
        
        if 'analyzers' not in kwargs or len(kwargs.get('analyzers')) == 0:
            raise('\'analyzers\' missing')
        
        cl_codes = list(map(lambda x: list(x), dbAPI.get_distinct_cl_codes()))
        options.update(kwargs.get('global_options', {}))
        
        analyzers = []
        for name, info in kwargs.get('analyzers').items():
            options_copy = options.copy()
            options_copy.update(info.get('options', {}))
            if options_copy.get('cl_codes') == 'all':
                options_copy['cl_codes'] = cl_codes
            if not isinstance(options_copy['cl_codes'], list):
                raise Exception("cl_codes must be an array")
            if len(list(filter(lambda x: x not in cl_codes, options_copy['cl_codes']))) > 0:
                raise Exception("some cl_codes are invalid")
            if name == "PagesSimilarity":
                analyzers.extend([PagesSimilarityAnalyzer(c_code=cl_code[0], l_code=cl_code[1], n=options_copy['n']) for cl_code in options_copy['cl_codes']])
            elif name == "UserSimilarity":
                step_size = int(options_copy.get("step_size"))
                import pandas as pd
                analyzers.extend([UsersSimilarityAnalyzer(data=pd.DataFrame(dbAPI.get_interactive_by_clcodes(cl_code[0], cl_code[1]), columns=['user_uid', 'worksheet_uid', 'l_code', 'c_code', 'time']), step_size=step_size, c_code=cl_code[0], l_code=cl_code[1]) for cl_code in options_copy['cl_codes']])
            elif name == "MostPopular":
                analyzers.extend([MostPopular(c_code=cl_code[0], l_code=cl_code[1]) for cl_code in options_copy['cl_codes']])
            elif name == "MarkovModel":
                analyzers.extend([MarkovAnalyzer(c_code=cl_code[0], l_code=cl_code[1]) for cl_code in options_copy['cl_codes']])
            else:
                raise Exception(f"Analyzing job named, {name} does not exist")
        
        return analyzers
            
            
            
        
        
        
        
            
