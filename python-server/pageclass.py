import dbAPI

class Worksheet:
    
    def __init__(self, worksheet_uid, c_code, l_code) -> None:
        self.worksheet_uid = worksheet_uid
        self.c_code = c_code
        self.l_code = l_code
        self.topics = None
        self.rec = None
        
    def build_page(self):
        res = dbAPI.get_page_topics_by_uid([self.worksheet_uid])
        self.topics = ','.join([t[1] for t in res])
    
    def get_rec(self, n):
        res = dbAPI.get_recommendations_for_worksheet(self.worksheet_uid, self.l_code, self.c_code) if self.rec == None else self.rec
        res = res.split(sep=",")
        
        self.rec = res
        
        n = min(len(res), n)
        res = res[:n]
            
        return res