import unittest
import pandas as pd
import numpy as np
import dbAPI
from models import CosUserSimilarityModel

class TestIsListOfStrings(unittest.TestCase):
    def test_user_similarity_model(self):
        import datetime
        t = datetime.datetime.now()
        train_size = 0.8
        # cl_codes = dbAPI.get_distinct_country_lang()
        for (c_code, l_code) in [("IL", "he")]:
            model = CosUserSimilarityModel(c_code, l_code)
            print(datetime.datetime.now()-t)
            data = pd.DataFrame(dbAPI.get_interactive_by_clcodes(c_code, l_code), columns=['user_uid', 'worksheet_uid', 'c_code', 'l_code', 'time'])
            print(datetime.datetime.now()-t)
            data = data.drop(columns=['c_code', 'l_code']).drop_duplicates()
            counts = data.groupby(by=['user_uid'], sort=False).count().reset_index()
            counts = counts[counts['time']>1]
            counts = counts['user_uid'].to_numpy()
            np.random.shuffle(counts)
            print(datetime.datetime.now()-t)
            
            train_size = int(counts.size*train_size)
            train_users, test_users = counts[:train_size], counts[train_size:] 
            train_data, test_data = data[data['user_uid'].isin(train_users)].copy(), data[data['user_uid'].isin(test_users)].copy()
            print(datetime.datetime.now()-t)
            model.fit(data=train_data, step_size=5)
            print(datetime.datetime.now()-t)

            test_data['time'] = pd.to_datetime(test_data['time'], format="%Y-%m-%d %H:%M:%S")
            test_data = test_data.sort_values(by=['user_uid', 'time'], ascending=[True, False])
            test_data = test_data.groupby(by=['user_uid'], sort=False, group_keys=False)[['worksheet_uid']].apply(lambda g: g['worksheet_uid'].to_numpy())
            test_data = test_data.to_numpy()
            
            data_max_len = max([d.size for d in test_data])
            test_data = np.array([np.pad(array=d, pad_width=(data_max_len-len(d),0), constant_values=[0]) for d in test_data])
            
            test_X, test_Y = test_data[:, :-1], test_data[:, -1:].flatten()
            
            predictions = model.predict(test_X).flatten()
            print(predictions.shape, test_Y.shape)
            accuracy = predictions[predictions].size/test_Y.size
            # print(accuracy)

if __name__ == '__main__':
    unittest.main()