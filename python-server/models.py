import pandas as pd
import numpy as np
import datetime
import json
from analyticsOnExcel import interactive_user_similarity_analysis, markov, popular_in_month
from sklearn.metrics.pairwise import cosine_similarity

from filter_manager import FilterFactory
from sklearn.preprocessing import normalize


class MyModel:    
    def __init__(self, c_code, l_code) -> None:
        self.c_code = c_code
        self.l_code = l_code
        
    def predict(self, data, **kwargs):
        pass
    
    def fit(self, **kwargs):
        pass
    
class CosUserSimilarityModel(MyModel):
    def __init__(self, c_code: str, l_code: str) -> None:
        """
        Initialize the CosUserSimilarityModel with the given country and language codes.

        Parameters:
        c_code (str): The country code.
        l_code (str): The language code.
        """
        super().__init__(c_code, l_code)
        
    def predict(self, data: list, **kwargs) -> np.ndarray:
        """
        Predict the next steps for the user based on the similarity of their history to other users.

        This method reads user similarity data from a Parquet file, calculates cosine similarity scores
        between the target user's history and other users' histories, and returns the top recommendations.

        Parameters:
        data (list): List of worksheet UIDs recommended in the last 5 interactions.
        kwargs: Additional keyword arguments:
            already_watched (list): List of pages already watched by the user, which will be excluded from the recommendations.

        Returns:
        np.ndarray: An array of pairs containing worksheet UIDs and their respective user scores as calculated by the algorithm.
        """
        # Read the User similarity parquet for the given language code, filtering by the provided data
        users = pd.read_parquet(f'UserSimilarityParquets/{self.l_code}.parquet', filters=[('0', 'in', data)])['user_uid'].unique()
        
        # If no similar users are found, return an empty array
        if len(users) == 0:
            return np.reshape(np.array([]), (-1, 2))
        
        # Read the parquet file again, this time filtering by the similar users found
        df = pd.read_parquet(f'UserSimilarityParquets/{self.l_code}.parquet', filters=[('user_uid', 'in', users)]).set_index('user_uid')
        
        # Create a one-hot encoded matrix for the users' histories
        Y = pd.get_dummies(df, prefix="", prefix_sep="").groupby(level=0).max()
        X = pd.DataFrame(0, index=[1], columns=Y.columns)
        
        # If no columns are found, return an empty array
        if X.shape[1] == 0:
            return np.reshape(np.array([]), (-1, 2))
        
        # Set the columns that are in the target user's history to 1
        X.loc[1, Y.columns[Y.columns.isin(data)]] = 1
        
        # Calculate the cosine similarity between the target user and other users
        cos_sim = cosine_similarity(X.values, Y.values)
        cos_sim = pd.DataFrame(cos_sim, index=[1], columns=Y.index)
        cos_sim = cos_sim.T.reset_index()
        
        df = df.reset_index()
        
        # Merge the cosine similarity scores with the users' histories
        df = pd.merge(df, cos_sim, how='left', right_on='user_uid', left_on='user_uid').sort_values(by=[1, 'user_uid'], ascending=[False, False]).drop_duplicates(subset=['0', 1], keep='first')
        
        # Return the worksheet UIDs and their respective similarity scores
        return df[['0', 1]].to_numpy()
    
    def fit(self, **kwargs) -> None:
        """
        Fit the model by processing and analyzing user similarity data.

        This method prepares the data for user similarity analysis by calling the `interactive_user_similarity_analysis`
        function. The data is processed into a suitable format for the model.

        Parameters:
        kwargs: Additional keyword arguments:
            data (pd.DataFrame): The input DataFrame containing user interaction data.
            step_size (int): The step size used to segment user histories. Default is 5.

        Raises:
        Exception: If 'data' is not provided in kwargs.
        """
        data = kwargs.get('data')
        step_size = kwargs.get('step_size', 5)
        
        if data is None:
            raise Exception('Needs data to fit to')
        
        interactive_user_similarity_analysis(data, step_size, self.c_code, self.l_code)
        
class CosPageSimilarityModel(MyModel):
    def __init__(self, c_code: str, l_code: str) -> None:
        """
        Initialize the CosPageSimilarityModel with the given country and language codes.

        Parameters:
        c_code (str): The country code.
        l_code (str): The language code.
        """
        super().__init__(c_code, l_code)
        
    def predict(self, data: list, **kwargs) -> np.ndarray:
        """
        Predict the top page recommendations based on page similarity.

        This method reads the top page recommendations for the specified worksheet UID from a Parquet file
        and returns the top recommendations based on page similarity.

        Parameters:
        data (list): List of worksheet UIDs recommended in the last interactions.
        kwargs: Additional keyword arguments (not used in this method).

        Returns:
        np.ndarray: An array of pairs containing worksheet UIDs and their respective similarity scores.
        """
        # Load the Parquet file containing the top recommendations by worksheet UID
        df = pd.read_parquet(f'top_by_country_files/{self.l_code}-{self.c_code}.parquet', filters=[('worksheet_uid', '==', data[-1])])
        
        # Extract the top recommendations for the last worksheet UID in the data
        top_recs = json.loads(df.loc[data[-1], 'top_10'])
        
        # Reshape the recommendations into a numpy array
        top_recs_array = np.reshape(np.array(top_recs), (-1, 2))
        
        return top_recs_array
        
    def fit(self, **kwargs) -> None:
        """
        Fit the model (not implemented).

        This method is a placeholder for fitting the model. In this implementation, it does nothing.

        Parameters:
        kwargs: Additional keyword arguments (not used in this method).

        Returns:
        None
        """
        pass

    
class MarkovModel(MyModel):
    def __init__(self, c_code: str, l_code: str, n: int) -> None:
        """
        Initialize the MarkovModel with the given country code, language code, and number of predictions.

        Parameters:
        c_code (str): The country code.
        l_code (str): The language code.
        n (int): The number of predictions to return.
        """
        super().__init__(c_code, l_code)
        self.N = n
    
    def predict(self, data: list, **kwargs) -> np.ndarray:
        """
        Predict the next steps for the user based on the Markov model.

        This method reads the Markov model results from a Parquet file, identifies the top recommendations
        based on the last worksheet clicked by the user, normalizes the scores, and returns the predictions.

        Parameters:
        data (list): List of worksheet UIDs representing the user's interaction history.
        kwargs: Additional keyword arguments (not used in this method).

        Returns:
        np.ndarray: An array of pairs containing worksheet UIDs and their respective scores.
        """
        # Last worksheet the user clicked
        last_page = data[-1]
        
        # Reading Markov model results from the Parquet file for the given language code
        df = pd.read_parquet(f"MarkovModelParquets/{self.l_code}.parquet", filters=[('worksheet_uid', '==', last_page)])
        
        if df.empty:
            return np.full((1, 2), -1)
        # Reshape the results to ensure they are in the correct format
        res = np.reshape(df, (-1, 2))
        
        # Normalize the scores
        res[:, 1] = normalize(np.reshape(res[:, 1], (1,-1))).flatten()
        
        return res
    
    def fit(self, **kwargs) -> None:
        """
        Fit the Markov model by processing and analyzing user interaction data.

        This method prepares the data for the Markov model analysis by calling the `markov` function.
        The data is processed into a suitable format for the model.

        Parameters:
        kwargs: Additional keyword arguments:
            data (pd.DataFrame): The input DataFrame containing user interaction data.

        Raises:
        Exception: If 'data' is not provided in kwargs or is not an instance of pd.DataFrame.
        """
        data = kwargs.get('data')
        
        if data is None or not isinstance(data, pd.DataFrame):
            raise Exception("'data' is not in kwargs or not instance of pd.DataFrame")
        
        # Call the markov function to process and analyze the user interaction data
        markov(data, self.c_code, self.l_code)

        
        
class MostPopularModel(MyModel):
    def __init__(self, c_code: str, l_code: str) -> None:
        """
        Initialize the MostPopularModel with the given country and language codes.

        Parameters:
        c_code (str): The country code.
        l_code (str): The language code.
        """
        super().__init__(c_code, l_code)
    
    def fit(self, **kwargs) -> None:
        """
        Fit the model by processing and analyzing user interaction data.

        This method prepares the data for popularity analysis by calling the `popular_in_month` function.
        The data is processed into a suitable format for the model.

        Parameters:
        kwargs: Additional keyword arguments:
            data (pd.DataFrame): The input DataFrame containing user interaction data.

        Returns:
        None
        """
        popular_in_month(kwargs.get('data'), self.c_code, self.l_code)
    
    def predict(self, data: None, **kwargs) -> np.ndarray:
        """
        Generate a list of the most popular pages within the same language, picked grades, and picked months.

        This method filters the most popular pages based on the specified grades and months, and returns the top N pages.

        Parameters:
        data (None): Not relevant for this method.
        kwargs: Additional keyword arguments:
            filters (dict): A dictionary containing filters for grades and months.

        Returns:
        np.ndarray: A numpy array with shape (n, 2) containing pairs of worksheet UIDs and their normalized counts.
        """
        return self.most_popular_in_month(**kwargs)
    
    def most_popular_in_month(self, **kwargs) -> np.ndarray:
        """
        Retrieve the most popular pages based on the specified filters.

        This method reads the popularity data from a Parquet file, applies the specified filters,
        and returns the top N most popular pages with their counts normalized.

        Parameters:
        kwargs: Additional keyword arguments:
            n (int, optional): The number of top pages to return. Default is 20.
            filters (dict): A dictionary containing filters for grades and months.

        Returns:
        np.ndarray: A numpy array with shape (n, 2) containing pairs of worksheet UIDs and their normalized counts.
        """
        # Get the number of top pages to return, defaulting to 20 if not provided.
        N = kwargs.get('n', 20)

        # Get the filters from the keyword arguments.
        filters = kwargs.get('filters', {})

        # Create a filter instance using the FilterFactory based on the provided filters.
        filter_instance = FilterFactory.create_instance(**filters)

        # Check if the country code and language code are provided. Raise an exception if they are not.
        if not self.c_code or not self.l_code:
            raise Exception('c_code and l_code must be sent in JSON body')

        # Read the popularity data from the Parquet file for the given country and language codes.
        df = filter_instance.run(pd.read_parquet(f'most_populars/{self.c_code}-{self.l_code}.parquet'))

        # Group the DataFrame by worksheet UID and sum the counts.
        df = df.groupby('worksheet_uid', group_keys=False)['count'].sum().reset_index().sort_values(by='count', ascending=False)

        # Convert the DataFrame to a numpy array and reshape it to have pairs of worksheet UIDs and counts.
        df: np.ndarray = np.reshape(df[['worksheet_uid', 'count']].head(N).to_numpy(), (-1, 2))

        # Normalize the counts by dividing them by the maximum count.
        df[:,1] = normalize(np.reshape(df[:, 1], (1,-1))).flatten()
        # Return the array of top recommendations.
        return df
    
    
class MixedModel(MyModel):
    def __init__(self, c_code, l_code, n) -> None:
        """
        Initialize the MixedModel with the given country and language codes and number of predictions.

        Parameters:
        c_code (str): The country code.
        l_code (str): The language code.
        n (int): The number of predictions to return.
        """
        super().__init__(c_code, l_code)
        self.N = n
    
    def fit(self, **kwargs):
        """
        Fit the model (not implemented).

        This method is a placeholder for fitting the model. In this implementation, it does nothing.

        Parameters:
        kwargs: Additional keyword arguments (not used in this method).

        Returns:
        None
        """
        pass
    
    def predict(self, data, **kwargs) -> pd.DataFrame:
        """
        Generate recommendations by combining results from multiple recommendation models.

        This method combines recommendations from Markov, user similarity, most popular, and page similarity models,
        and returns the top recommendations based on a weighted sum of their scores.

        Parameters:
        data (list): List of worksheet UIDs representing the user's interaction history.
        kwargs: Additional keyword arguments:
            grade (list, optional): A list of grades to filter the most popular recommendations.
            score_above (float, optional): Minimum score threshold for recommendations.
            n (int, optional): The number of top recommendations to return. Default is 10.

        Returns:
        pd.DataFrame: A DataFrame containing the top recommendations with their combined scores.
        """
        # Define the weights for each model's scores
        markov_per, us_per, mp_per, ps_per = kwargs.get('markov_per', 0.32), kwargs.get('us_per', 0.32), kwargs.get('mp_per', 0.05), kwargs.get('ps_per', 0.32)
        
        # Initialize the Markov model and get its recommendations
        markov_model = MarkovModel(self.c_code, self.l_code, self.N)
        markov_res = markov_model.predict(data)
        
        # Initialize the user similarity model and get its recommendations
        us_model = CosUserSimilarityModel(self.c_code, self.l_code)
        us_res = us_model.predict(data, n=self.N)
        
        # Initialize the most popular model and get its recommendations with filters
        mp_model = MostPopularModel(self.c_code, self.l_code)
        filters = {
            'MonthFilter': {'months': list(range(1, 13))}
        }
        if kwargs.get('grade'):
            filters['AgeFilter'] = {'ages': kwargs.get('grade')}
        mp_res = mp_model.predict(data, n=100, filters=filters)
        
        # Initialize the page similarity model and get its recommendations
        ps_model = CosPageSimilarityModel(self.c_code, self.l_code)
        ps_res = ps_model.predict(data)
        
        # Combine all recommendations into a single DataFrame
        res = pd.DataFrame(0, index=np.concatenate((markov_res[:, 0], us_res[:, 0], mp_res[:, 0], ps_res[:, 0])), 
                           columns=['markov_score', 'us_score', 'mp_score', 'ps_score'], dtype='float64')
        res = res.reset_index(names='worksheet_uid').drop_duplicates().set_index('worksheet_uid')
        
        # Assign scores from each model to the DataFrame
        res.loc[markov_res[:, 0], 'markov_score'] = markov_res[:, 1].astype('float64') * markov_per
        res.loc[us_res[:, 0], 'us_score'] = us_res[:, 1].astype('float64') * us_per
        res.loc[mp_res[:, 0], 'mp_score'] = mp_res[:, 1].astype('float64') * mp_per
        res.loc[ps_res[:, 0], 'ps_score'] = ps_res[:, 1].astype('float64') * ps_per
        
        # Calculate the combined score for each recommendation
        res['score'] = res.sum(axis=1)
        
        # Sort recommendations by the combined score in descending order
        res = res.sort_values(by='score', ascending=False)
        
        # Filter recommendations with scores above the specified threshold
        res = res[res['score'] > kwargs.get('score_above', 0)]
        
        # Select the top N recommendations
        res = res.head(kwargs.get('n', 10))
        
        return res

class TCNRecommender(MyModel):
    def __init__(self, c_code, l_code) -> None:
        super().__init__(c_code, l_code)
        
    def predict(self, data, **kwargs):
        pass
    
    def fit(self, **kwargs):
        data = kwargs.get('data')
        if data is None or not isinstance(data, pd.DataFrame):
            raise Exception("Must send 'data' in kwargs")
        

        
        