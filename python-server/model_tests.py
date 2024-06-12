import numpy as np
import pandas as pd
from models import MyModel



def test_my_model(data: pd.DataFrame | np.ndarray, model: MyModel, iterations=3, name='accuracy',):
    if not isinstance(data, (pd.DataFrame, np.ndarray)):
        raise Exception(f"data argument should be of instance {type(pd.DataFrame())} or {type(np.ndarray())}")
    if isinstance(data, pd.DataFrame):
        data = pd.DataFrame.to_numpy()
    
    train_X, train_Y, test_X, test_Y = split_train_test(data)
    model.fit(train_X, train_Y)
    predictions = model.predict(test_X)
    accuracy = predictions[predictions==test_Y]/test_Y.size
    return accuracy

def split_train_test(data: np.ndarray, train_p: 0.8):
    if train_p >=1:
        raise Exception(f"train_p must be between (0,1)")
    np.random.shuffle(data)
    data_max_len = max([len(d) for d in data])
    data = np.array([np.pad(array=d, pad_width=(data_max_len-len(d),0), constant_values=[0]) for d in data])
    train_size = int(data.size*train_p)
    train_data, test_data = data[:train_size], data[train_size:]
    
    train_X, train_Y, test_X, test_Y = train_data[:, :-1], train_data[:, -1:].flatten(), test_data[:, :-1], test_data[:, -1:].flatten()
    return train_X, train_Y, test_X, test_Y