import sys
sys.path.append('.')
import dbAPI
import unittest
import pandas as pd
import numpy as np
from models import CosUserSimilarityModel, MarkovModel, MostPopularModel, MixedModel, CosPageSimilarityModel


class TestModels(unittest.TestCase):
    
    def test_user_similarity(self):
        c_code = "IL"
        l_code = "he"
        
        worksheet_uid = '19b3cde4'
        
        model = CosUserSimilarityModel(c_code, l_code)
        
        res = model.predict([worksheet_uid])
        
        self.assertEqual(res.shape[1], 2, f'Shape columns is {res.shape[1]} and not 2')
        
        self.assertGreater(res.shape[0], 0, f"recommendations shape is: {res.shape} and has less than 0 rows")
        
        worksheet_uid = '1'
        res = model.predict([worksheet_uid])
        
        self.assertEqual(res.shape, (0,2), f'Shape should be (0,2) but is {res.shape}')
        
    
    def test_markov(self):
        c_code = "IL"
        l_code = "he"
        
        worksheet_uid = '19b3cde4'
        
        model = MarkovModel(c_code, l_code, 10)
        
        res = model.predict([worksheet_uid])
        
        self.assertEqual(res.shape[1], 2, f'Shape columns is {res.shape[1]} and not 2')
        
        self.assertGreater(res.shape[0], 0, f"recommendations shape is: {res.shape} and has less than 0 rows")
        
        worksheet_uid = '1'
        res = model.predict([worksheet_uid])
        
        self.assertEqual(res.shape, (0,2), f'Shape should be (0,2) but is {res.shape}')
    
    def test_most_popular(self):
        pass
    
    def test_page_similarity(self):
        c_code = "IL"
        l_code = "he"
        
        worksheet_uid = '19b3cde4'
        
        model = CosPageSimilarityModel(c_code, l_code)
        
        res = model.predict([worksheet_uid])
        
        self.assertEqual(res.shape[1], 2, f'Shape columns is {res.shape[1]} and not 2')
        
        self.assertGreater(res.shape[0], 0, f"recommendations shape is: {res.shape} and has less than 0 rows")
        
        worksheet_uid = '1'
        res = model.predict([worksheet_uid])
        
        self.assertEqual(res.shape, (0,2), f'Shape should be (0,2) but is {res.shape}')
    
    def test_mixed_model(self):
        c_code = "IL"
        l_code = "he"
        
        worksheet_uid = '19b3cde4'
        
        model = MixedModel(c_code, l_code, 10)
        
        res = model.predict([worksheet_uid])
        
        self.assertEqual(res.shape[1], 5, f'Shape columns is {res.shape[1]} and not 2')
        
        self.assertGreater(res.shape[0], 0, f"recommendations shape is: {res.shape} and has less than 0 rows")
        
        worksheet_uid = '1'
        res = model.predict([worksheet_uid])
        
        self.assertGreater(res.shape[0], 0, f'Shape should be (0,2) but is {res.shape}')
        
    
    def test_update_recommendations(self):
        import os
        os.system('rm -rf MarkovModelParquets most_populars top_by_country_files UserSimilarityParquets')
        
        import service
        body = {
            "analyzers": {
                "UserSimilarity": {},
                "PagesSimilarity": {},
                "MarkovModel": {},
                "MostPopular": {}
            }
        }
        
        self.assertIsNone(service.update_files_recommendations(body))
        dirs_names = ["MarkovModelParquets",
                      "most_populars",
                      "top_by_country_files",
                      "UserSimilarityParquets"]
        dirs_exist = list(map(lambda dir_name: os.path.exists(dir_name), dirs_names))
        self.assertTrue(np.all(dirs_exist))
        
        dirs_items = list(map(lambda dir_name: os.listdir(dir_name), dirs_names))
        
        dirs_count = list(map(lambda dir_items: len(dir_items), dirs_items))
        
        dirs_should_be_count = [8, 59, 59, 8]
        
        self.assertEqual(dirs_count, dirs_should_be_count)
        print(dirs_count)
        

if __name__ == '__main__':
    unittest.main()