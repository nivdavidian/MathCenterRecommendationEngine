from functools import reduce
import dbAPI
from pageclass import Worksheet
from analyzer import AnalyzerFactory
from wrapper import wrap
import numpy as np

from models import MarkovModel, MostPopularModel, CosUserSimilarityModel, MixedModel, CosPageSimilarityModel

def recommend(uids, n=20, c_code="IL", l_code="he"):
    """
    Generate worksheet recommendations based on page similarity.

    This function uses the CosPageSimilarityModel to predict similar worksheets
    for the given user history UIDs. It sorts the predictions by similarity scores
    in descending order, retrieves detailed information for the recommended worksheets,
    and returns the top recommendations.

    Parameters:
    uids (list of str): The UIDs of the user's history.
    n (int, optional): The number of recommendations to return. Default is 20.
    c_code (str, optional): The country code. Default is "IL".
    l_code (str, optional): The language code. Default is "he".

    Returns:
    list: A list of dictionaries containing information about the recommended worksheets.
    """
    
    # Initialize the CosPageSimilarityModel with the specified country and language codes
    model = CosPageSimilarityModel(c_code, l_code)
    
    # Predict similar worksheets based on the user history UIDs
    preds = model.predict(uids)
    
    # Sort the predictions by similarity scores in descending order
    preds = preds[np.argsort(preds[:, 1])[::-1]]
    
    # Retrieve detailed information for the recommended worksheets
    infos = get_worksheets_info(preds[:, 0], c_code, l_code)
    
    # Return the top recommendations with detailed information
    return [infos[uid] for uid in preds[:, 0]]

def recommend_users_alike(already_watched, worksheet_uids, c_code, l_code, **kwargs):
    """
    Generate worksheet recommendations based on user similarity.

    This function uses the CosUserSimilarityModel to predict similar worksheets for the given user history
    and a list of worksheet UIDs. It sorts the predictions by similarity scores in descending order,
    retrieves detailed information for the recommended worksheets, and returns the top recommendations.

    Parameters:
    already_watched (list of str): The UIDs of worksheets already watched by the user.
    worksheet_uids (list of str): The UIDs of worksheets to consider for recommendations.
    c_code (str): The country code.
    l_code (str): The language code.
    **kwargs: Additional keyword arguments:
        n (int, optional): The number of recommendations to return. Default is 20.
        cCode (str, optional): Override for the country code for fetching worksheet info.
        lCode (str, optional): Override for the language code for fetching worksheet info.

    Returns:
    list: A list of dictionaries containing information about the recommended worksheets.
    """
    
    # Initialize the CosUserSimilarityModel with the specified country and language codes
    model = CosUserSimilarityModel(c_code, l_code)
    
    # Predict similar worksheets based on the user history and specified worksheet UIDs
    preds = model.predict(worksheet_uids, already_watched=already_watched, n=kwargs.get('n', 20))
    
    # Sort the predictions by similarity scores in descending order
    preds = preds[np.argsort(preds[:, 1])[::-1]]
    
    # Retrieve detailed information for the recommended worksheets
    infos = get_worksheets_info(preds[:, 0], kwargs.get('cCode', c_code), kwargs.get('lCode', l_code))
    
    # Return the top recommendations with detailed information
    return [infos[uid] for uid in preds[:, 0]]

def update_files_recommendations(json):
    analyzers = AnalyzerFactory.create_instance(**json)
    wrapper = wrap(analyzers)
    wrapper.run()
    
def most_popular_in_month(**kwargs):
    """
    Retrieve the most popular worksheets for a given month.

    This function uses the MostPopularModel to predict the most popular worksheets based on
    the specified filters. It sorts the predictions by popularity scores in descending order,
    retrieves detailed information for the recommended worksheets, and returns the top recommendations.

    Parameters:
    **kwargs: Additional keyword arguments:
        cCode (str): The country code.
        lCode (str): The language code.
        AgeFilter (list of str, optional): A list of grades to filter the worksheets by age group.
                                           Possible values: ['first', 'second', 'third', ..., 'eighth'].
        MonthFilter (list of int, optional): A list of months (1-12) to filter the worksheets by popularity in specific months.

    Returns:
    list: A list of dictionaries containing information about the most popular worksheets.
    """
    
    # Initialize the MostPopularModel with the specified country and language codes
    model = MostPopularModel(kwargs.get('cCode'), kwargs.get('lCode'))
    
    # Predict the most popular worksheets based on the specified filters
    preds = model.predict(None, **kwargs)
    
    # Sort the predictions by popularity scores in descending order
    preds = preds[np.argsort(preds[:, 1])[::-1]]
    
    # Retrieve detailed information for the recommended worksheets
    infos = get_worksheets_info(preds[:, 0], kwargs.get('cCode'), kwargs.get('lCode'))
    
    # Return the top recommendations with detailed information
    return [infos[uid] for uid in preds[:, 0]]
    
    
def get_worksheets_info(uids, c_code, l_code):
    """
    Retrieve detailed information for a list of worksheet UIDs.

    This function queries the database for information about the specified worksheets,
    aggregates the topics associated with each worksheet, and returns a dictionary
    containing the detailed information for each worksheet.

    Parameters:
    uids (list of str): The UIDs of the worksheets to retrieve information for.
    c_code (str): The country code.
    l_code (str): The language code.

    Returns:
    dict: A dictionary where each key is a worksheet UID and the value is another dictionary containing:
        - 'uid' (str): The UID of the worksheet.
        - 'topics' (list of str): A list of topics associated with the worksheet.
        - 'min_grade' (int): The minimum grade level for which the worksheet is suitable.
        - 'max_grade' (int): The maximum grade level for which the worksheet is suitable.
        - 'name' (str): The title of the worksheet.
    """
    
    # Query the database for worksheet information
    infos = dbAPI.get_worksheet_info(uids, c_code, l_code)
    
    # Initialize a dictionary to store the aggregated worksheet information
    m = {}
    
    # Iterate through the retrieved information
    for row in infos:
        uid, topic, min_grade, max_grade, title = row
        
        # Aggregate topics for each worksheet UID
        if uid in m:
            m[uid]['topics'].append(topic)
        else:
            m[uid] = {'uid': uid, 'topics': [topic], 'min_grade': min_grade, 'max_grade': max_grade, 'name': title}
    
    return m
    
def predict_markov(worksheet_uid, c_code, l_code, n, **kwargs):
    """
    Generate worksheet recommendations based on the Markov model.

    This function uses the Markov model to predict similar worksheets for a given worksheet UID.
    It sorts the predictions by their scores in descending order, retrieves detailed information
    for the recommended worksheets, and returns the top recommendations.

    Parameters:
    worksheet_uid (str): The UID of the worksheet to generate recommendations for.
    c_code (str): The country code.
    l_code (str): The language code.
    n (int): The number of recommendations to return.
    **kwargs: Additional keyword arguments:
        grade (list of str, optional): A list of grades to filter the recommendations.
        cCode (str, optional): Override for the country code for fetching worksheet info.
        lCode (str, optional): Override for the language code for fetching worksheet info.

    Returns:
    list: A list of dictionaries containing information about the recommended worksheets.
    """
    
    # Initialize the MarkovModel with the specified country code, language code, and number of recommendations
    model = MarkovModel(c_code, l_code, n)
    
    # Predict similar worksheets based on the provided worksheet UID
    preds = model.predict(worksheet_uid, n=n, grade=kwargs.get('grade'))
    
    # Sort the predictions by their scores in descending order
    preds = preds[np.argsort(preds[:, 1])[::-1]]
    
    # Retrieve detailed information for the recommended worksheets
    infos = get_worksheets_info(preds[:, 0], kwargs.get('cCode', c_code), kwargs.get('lCode', l_code))
    
    # Return the top recommendations with detailed information
    return [infos[uid] for uid in preds[:, 0]]


def predict_mixed(uids, c_code, l_code, n, score_above, **kwargs):
    """
    Generate recommendations using a mixed model algorithm.

    This function uses the MixedModel to predict recommendations based on multiple algorithms.
    It sorts the predictions by their scores in descending order, retrieves detailed information
    for the recommended worksheets, and returns the top recommendations.

    Parameters:
    uids (list of str): The UIDs of the user's history.
    c_code (str): The country code.
    l_code (str): The language code.
    n (int): The number of recommendations to return.
    score_above (float): The score threshold for filtering recommendations.
    **kwargs: Additional keyword arguments:
        grade (list of str, optional): A list of grades to filter the recommendations.

    Returns:
    list: A list of dictionaries containing information about the recommended worksheets.
    """
    
    # Initialize the MixedModel with the specified country code, language code, and number of recommendations
    model = MixedModel(c_code, l_code, n)
    
    # Predict recommendations based on the user's history and additional filters
    preds_df = model.predict(uids, n=n, grade=kwargs.get('grade'), score_above=score_above)
    
    # If no predictions are returned, return an empty list
    if preds_df.empty:
        return []
    
    # Extract all UIDs from the predictions
    all_uids = list(preds_df.index)
    
    # Retrieve detailed information for the recommended worksheets
    infos = get_worksheets_info(all_uids, c_code, l_code)
    
    # Combine the information and prediction scores into a single list, sorted by score in descending order
    return sorted(
        list(map(lambda x: {**infos[x[0]], **x[1]}, preds_df.T.to_dict().items())), 
        key=lambda x: x['score'], 
        reverse=True
    )