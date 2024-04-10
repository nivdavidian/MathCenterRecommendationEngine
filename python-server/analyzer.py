from factory import AbstractFactory
from abc import ABC, abstractmethod
from analyticsOnExcel import analyze_interactive, task
from wrapper import Wrapper
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
        self.c_code = kwargs.get('c_code')
        self.l_code = kwargs.get('l_code')
        self.step_size = kwargs.get('step_size')
    
    def analyze(self):
        analyze_interactive(self.c_code, self.l_code, step=self.step_size)
    def run(self):
        super().run(self.analyze)
    
    

class AnalyzerFactory(AbstractFactory):
    
    @classmethod
    def create_instance(cls, **kwargs):
        options = {
            'cl_codes': 'all', 
            'n': 50,
        }
        analyzers_info = kwargs.get("analyzers_info")
        
        if not analyzers_info:
            raise Exception("Need to send analyzers_info as argument (analyzers_info=?:dict)")
        if not isinstance(analyzers_info, dict):
            raise Exception("analyzers_info of not type dict")
        if 'analyzers' not in analyzers_info or len(analyzers_info.get('analyzers')) == 0:
            raise('\'analyzers\' key missing in analyzers_info or is empty')
        
        cl_codes = list(map(lambda x: list(x), dbAPI.get_distinct_cl_codes()))
        options.update(analyzers_info.get('global_options', {}))
        
        analyzers = []
        for name, info in analyzers_info.get('analyzers').items():
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
                step_size = int(options_copy.get("step_size", 5))
                analyzers.extend([UsersSimilarityAnalyzer(c_code=cl_code[0], l_code=cl_code[1], step_size=step_size) for cl_code in options_copy['cl_codes']])
            else:
                raise Exception(f"Analyzing job named, {name} does not exist")
        
        return analyzers
            
            
            
        
        
        
        
            
