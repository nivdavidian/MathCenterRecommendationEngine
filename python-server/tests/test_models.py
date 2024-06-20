import sys
sys.path.append('.')
import dbAPI
import unittest
import pandas as pd
import numpy as np
from models import CosUserSimilarityModel, MarkovModel, MostPopularModel
from functools import reduce



class TestIsListOfStrings(unittest.TestCase):
    
    def test_markov_model(self):
        train_p = 0.85
        average = 0
        average_num = 0
        N = 10 # recall recommendation size
        
        cl_codes = dbAPI.get_distinct_country_lang()
        for (c_code, l_code) in cl_codes:
            # print(c_code, l_code)
            model = MarkovModel(c_code, l_code)
            popular_model = MostPopularModel(c_code, l_code)
            user_similarity_model = CosUserSimilarityModel(c_code, l_code)
            
            df = pd.DataFrame(dbAPI.get_interactive_by_clcodes(c_code, l_code), columns=['user_uid', 'worksheet_uid', 'c_code', 'l_code', 'time'])
            # print(df)
            
            df['time'] = pd.to_datetime(df['time'], format="%Y-%m-%d %H:%M:%S")
            df = df.sort_values(by=['user_uid', 'time'], ascending=[False, True]).reset_index(drop=True)
            df2 = df.shift(-1)
            
            df = df[(df2['user_uid'] == (df['user_uid'])) & (df2['worksheet_uid']!=(df['worksheet_uid']))].reset_index(drop=True)
            
            counts = df.groupby(by=['user_uid'], group_keys=False).count().reset_index()
            counts = counts[counts['time']>2]
            df = df[df['user_uid'].isin(counts['user_uid'])]
            del counts
            
            users = df['user_uid'].unique()
            np.random.shuffle(users)
            if len(users)<200:
                print(f'Has {len(users)} users only this is Not Enough')
                continue
            
            train_size = int(train_p*len(users))
            train_users, test_users = users[:train_size], users[train_size:]
            
            train_data, test_df = df[df['user_uid'].isin(train_users)].copy(), df[df['user_uid'].isin(test_users)].copy()
            
            model.fit(data=train_data)
            user_similarity_model.fit(data=train_data, step_size=10)
            popular_model.fit(data=train_data)
            test_df = test_df.sort_values(by=['user_uid', 'time'], ascending=[False, True]).groupby(by='user_uid', group_keys=False)[['worksheet_uid']].apply(lambda g: g['worksheet_uid'].to_list())
            np_test_df = test_df.to_numpy().tolist()
            # print(np_test_df)
            test_X, test_Y = [x[-2] for x in np_test_df], [x[-1] for x in np_test_df]
            
            import datetime
            t = datetime.datetime.now()
            predictions = model.predict(test_X, n=N)
            print(datetime.datetime.now() -t)
            
            score = 0
            for i, p in enumerate(predictions):
                if test_Y[i] in p:
                    score+=1
                
            print(f"markov ({c_code}-{l_code}) score: {score/len(test_X)}")
            average_num += 1
            average += score/len(test_X)
            
        print(f"Markov average: {average/average_num}")
            
    def test_user_similarity_model(self):
        # import datetime
        # t = datetime.datetime.now()
        N = 10
        train_p = 0.85
        cl_codes = dbAPI.get_distinct_country_lang()
        average = 0
        average_num = 0
        for (c_code, l_code) in cl_codes:
            model = CosUserSimilarityModel(c_code, l_code)
            popular_model = MostPopularModel(c_code, l_code)
            # print(datetime.datetime.now()-t)
            data = pd.DataFrame(dbAPI.get_interactive_by_clcodes(c_code, l_code), columns=['user_uid', 'worksheet_uid', 'c_code', 'l_code', 'time'])
            # print(datetime.datetime.now()-t)
            
            data['time'] = pd.to_datetime(data['time'], format="%Y-%m-%d %H:%M:%S")
            data = data.sort_values(by=['user_uid', 'time'], ascending=[False, True]).reset_index(drop=True)
            df2 = data.shift(-1)
            
            data = data[(df2['user_uid'] == (data['user_uid'])) & (df2['worksheet_uid']!=(data['worksheet_uid']))].reset_index(drop=True)
            
            data = data.drop_duplicates()
            counts = data.groupby(by=['user_uid'], sort=False).count().reset_index()
            counts = counts[counts['time']>2]
            counts = counts['user_uid'].to_numpy()
            np.random.shuffle(counts)
            # print(datetime.datetime.now()-t)
            
            if len(counts)<200:
                print(f'Has {len(counts)} users only this is Not Enough')
                continue
            
            train_size = int(counts.size*train_p)
            train_users, test_users = counts[:train_size], counts[train_size:] 
            train_data, test_data = data[data['user_uid'].isin(train_users)].copy(), data[data['user_uid'].isin(test_users)].copy()
            # print(datetime.datetime.now()-t)
            model.fit(data=train_data, step_size=30)
            popular_model.fit(data=train_data)
            # print(datetime.datetime.now()-t)

            test_data['time'] = pd.to_datetime(test_data['time'], format="%Y-%m-%d %H:%M:%S")
            test_data = test_data.sort_values(by=['user_uid', 'time'], ascending=[True, True])
            test_data = test_data.groupby(by=['user_uid'], sort=False, group_keys=False)[['worksheet_uid']].apply(lambda g: g['worksheet_uid'].to_list())
            test_data = test_data.to_list()
            # print(test_data)
            
            test_X, test_Y = [x[:-1] for x in test_data], [x[-1] for x in test_data]
            
            predictions = []
            for x in test_X:
                predictions.append(model.predict(x, n=N))
            
            score = 0
            for i, pred in enumerate(predictions):
                if test_Y[i] in pred:
                    score+=1
            print(f"User Similarity ({c_code}-{l_code}) score: {score/len(test_X)}")
            average_num += 1
            average += score/len(test_X)
        print(f'User Similarity average: {average/average_num}')

if __name__ == '__main__':
    unittest.main()