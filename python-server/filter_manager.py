import dbAPI
import pandas as pd

from factory import AbstractFactory

class FilterWrap:
    def __init__(self) -> None:
        self.next_filter: FilterWrap = None
    def run(self, data):
        data = self.filter(data)
        if self.next_filter:
            data = self.next_filter.run(data)
        return data

class Filter(FilterWrap):
    def __init__(self) -> None:
        super().__init__()
    def filter(self, df):
        pass
    def pre_process(self, df):
        if 'worksheet_list' in df.columns:
            df = df.explode("worksheet_list")
            df = df.rename(columns={"worksheet_list": "worksheet_uid"})
        return df
class AgeFilter(Filter):
    def __init__(self, **options) -> None:
        super().__init__()
        self.ages = options['ages']
    def filter(self, df):
        df = self.pre_process(df)
        try:
            selected_rows = df.loc[:, self.ages].any(axis=1)
            return df[selected_rows]
        except Exception as e:
            from recServer import logger
            logger.warning(f"warning in age filter: {e}")
        return df
    def pre_process(self, df):
        df = super().pre_process(df)
        return df
            
class MonthFilter(Filter):
    def __init__(self, **options) -> None:
        super().__init__()
        self.months = options['months']
    def filter(self, df):
        df = self.pre_process(df)
        return df[df['month'].isin(self.months)]
    def pre_process(self, df):
        df = super().pre_process(df)
        return df
        


class FilterFactory(AbstractFactory):
    
    @classmethod
    def create_instance(cls, **kwargs):
        filters = ['AgeFilter', 'MonthFilter']
        b = False
        for filter in filters:
            if filter in kwargs:
                b = True
                break     
        if not b:
            raise Exception(f"no filters are named.\n{kwargs}")
        
        filters = []
        for name, options in kwargs.items():
            if name == 'AgeFilter' and isinstance(options, dict):
                if 'ages' not in options:
                    raise Exception(f'Need to configure ages for AgeFilter')
                filters.append(AgeFilter(**options))
            elif name == 'MonthFilter' and isinstance(options, dict):
                if 'months' not in options:
                    raise Exception(f'Need to configure \'months\' for MonthFilter')
                filters.append(MonthFilter(**options))
        return build_wrapped_filters(filters)
                


def build_wrapped_filters(filters):
    first = filters[0]
    last = first
    for filter in filters[1:]:
        last.next_filter = filter
        last = filter
    return first