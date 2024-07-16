import dbAPI
import service
import time
import logging
from flask import Flask, request, jsonify, abort, g, make_response
from logging.handlers import RotatingFileHandler
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes and origins

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_handler = RotatingFileHandler('gunicorn.log', maxBytes=1024 * 1024 * 100, backupCount=20)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

@app.before_request
def before_request():
    g.start_time = time.time()
    logger.info(f'content Length:{request.content_length}')
    
@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    logger.info(f"{request.path} took {duration}")
    return response

@app.route("/api/getpages")
def get_pages():
    """
    Retrieve the names and UIDs of worksheets based on a specific language and country code.

    Parameters:
    term (str): The search term used to find similar titles.
    cCode (str): The country code.
    lCode (str): The language code.

    Returns:
    json: A list of dictionaries, each containing the UID of a worksheet as the key and a dictionary of worksheet details as the value.
    """
    try:
        term = request.args.get("term", "", type=str)
        c_code = request.args.get("cCode", "", type=str)
        l_code = request.args.get("lCode", "", type=str)
        print(request.args)
        results = dbAPI.get_recommend_search(term,l_code, c_code)
        if len(results) == 0:
            return jsonify([])
        results = service.get_worksheets_info([res[0] for res in results], c_code, l_code)
        return jsonify(list(results.values()))
    except Exception as e:
        logger.error(f"get Pages:\n{e}")
        return abort(500, "Error")

@app.route("/api/getclcodes")
def get_cl_codes():
    """
    Retrieve a list of unique country-language code pairs from the database.

    This function queries the database for distinct country and language codes,
    concatenates them into a single string separated by a hyphen (e.g., 'US-en'),
    and returns them as a JSON array. If an error occurs during the process,
    a 500 error is returned.

    Returns:
    json: A list of concatenated country-language code pairs.
    """
    try:
        codes = dbAPI.get_distinct_cl_codes()
        
        cl_codes = []
        for row in codes:
            c_code, l_code = row[0], row[1]
            cl_codes.append(f'{c_code}-{l_code}')
            
        return jsonify(cl_codes)
    except Exception as e:
        logger.error(f"get cl codes:\n{e}")
        return abort(500, "Error")
    
        
    
@app.route("/api/getrecommendation", methods=['POST'])
def get_recommendation():
    """
    Retrieve recommendations based on the Page Similarity algorithm.

    Parameters:
    uid (str): The UID of the worksheet used to find similar pages.
    cCode (str): The country code.
    lCode (str): The language code.

    Returns:
    json: A list of dictionaries, each containing the UID of a worksheet as the key and a dictionary of worksheet details as the value.
    """
    try:
        uids = request.json["uid"]
        c_code = request.json["cCode"]
        l_code = request.json["lCode"]
        rec = service.recommend(uids, c_code=c_code, l_code=l_code)
        return jsonify(rec)
    except Exception as e:
        logger.error(e)
        return abort(500, "Error")
    
        
@app.route("/api/recuseralike", methods=["POST"])
def get_recommendation_user():
    """
    Retrieve recommendations based on the User Similarity algorithm.

    This function receives the list of already watched worksheets, worksheet UIDs,
    country code, and language code from the request body. It uses these parameters
    to generate recommendations based on the similarity of users' watching behavior.

    Parameters:
    already_watched (list): A list of UIDs representing worksheets that have already been watched.
    worksheet_uids (list): A list of UIDs representing worksheets to consider for recommendations.
    cCode (str): The country code.
    lCode (str): The language code.

    Returns:
    json: A list of recommended worksheets, each represented by a dictionary containing
          the UID of the worksheet and additional details.
    """
    try:
        already_watched = request.json["already_watched"]
        worksheet_uids = request.json["worksheet_uids"]
        c_code = request.json["cCode"]
        l_code = request.json["lCode"]
        rec = service.recommend_users_alike(already_watched, worksheet_uids, c_code=c_code, l_code=l_code)
        return jsonify(rec)
    except Exception as e:
        logger.error(e)
        return abort(500, "Error")
    
@app.route('/api/updaterecommendations', methods=['POST'])
def update_recommendations():
    """
    Update the parquet files used by the recommendation algorithms.

    This function processes parameters received from the JSON body to update the parquet files
    for various recommendation algorithms.

    Parameters:
    analyzers (list of str): List of the names of algorithms whose parquet files need updating. 
                             Options: ['PagesSimilarity', 'UserSimilarity', 'MarkovModel', 'MostPopular']
    cl_codes (list of list of str): List of country-language code pairs (cl_codes) to update the parquet files for, 
                                    where each pair is represented as a list of two strings [country_code, language_code].
    n (int): The number of similar pages to save in the PagesSimilarity parquet file for each worksheet UID.
    step_size (int): The step size for segmenting user history; the segment size is twice the step_size.

    Returns:
    """
    try:
        service.update_files_recommendations(request.json)
        return make_response("OK", 200)
    except Exception as e:
        logger.error(e)
        return abort(500, "Error")

@app.route('/api/mostpopular', methods=['POST'])
def most_popular():
    """
    Retrieve the most popular worksheets for a given month and age filter.

    This function processes parameters received from the JSON body to fetch the most popular worksheets
    based on the specified age and month filters.

    Parameters (received in JSON body):
    AgeFilter (list of str, optional): A list of grades to filter the worksheets by age group. 
                                       Possible values: ['first', 'second', 'third', ..., 'eighth'].
    MonthFilter (list of int, optional): A list of months (1-12) to filter the worksheets by popularity in specific months.

    Returns:
    json: A list of recommended worksheets, each represented by a dictionary containing
          the UID of the worksheet and additional details.
    """
    try:
        populars = service.most_popular_in_month(**request.json)
        return jsonify(populars)
    except Exception as e:
        logger.error(e)
        return abort(500, "Error")
    
@app.route('/api/markov', methods=['POST'])
def markov():
    """
    Generate recommendations based on the Markov model algorithm.

    This function receives parameters from the JSON body to generate recommendations using the Markov model.
    It requires the UID of the worksheet, country code, and language code. Optionally, the number of recommendations
    to return can be specified.

    Parameters (received in JSON body):
    uid (str): The UID of the worksheet for which recommendations are to be generated.
    cCode (str): The country code.
    lCode (str): The language code.
    n (int, optional): The number of recommendations to return. Default is 10.

    Returns:
    json: A list of recommended worksheets, each represented by a dictionary containing
          the UID of the worksheet and additional details.
    """
    try:
        worksheet_uid = request.json['uid']
        c_code = request.json['cCode']
        l_code = request.json['lCode']
        n = 10
        if 'n' in request.json:
            n = request.json['n']
    except:
        return abort(500, 'missing argument/s in body: uid, cCode, lCode. n is optional')
    
    try:
        preds = service.predict_markov(worksheet_uid, c_code, l_code, n, **(request.json))
        return jsonify(preds)
    except Exception as e:
        logger.error(e)
        return abort(500, 'Error')
        
@app.route('/api/recmodel', methods=['POST'])
def recmodel():
    """
    Generate recommendations using a mixed model algorithm.

    This function combines multiple recommendation algorithms to generate better recommendations.
    It requires the UIDs of the user's history, country code, and language code. Optionally, the number of 
    recommendations, a score threshold, and grade filter can be specified.

    Parameters (received in JSON body):
    uids (list of str): The UIDs of the user's history.
    cCode (str): The country code.
    lCode (str): The language code.
    n (int, optional): The number of recommendations to return. Default is 10.
    scoreAbove (float, optional): The score threshold for filtering recommendations. Default is 0.
    grade (list of str, optional): A list of grades to filter recommendations.

    Returns:
    json: A list of recommended worksheets, each represented by a dictionary containing
          the UID of the worksheet and additional details.
    """
    try:
        uids = request.json['uids']
        c_code = request.json['cCode']
        l_code = request.json['lCode']
        n = 10 if 'n' not in request.json else int(request.json['n'])
        score_above = 0 if 'scoreAbove' not in request.json else float(request.json['scoreAbove'])
        grades = None if 'grade' not in request.json else request.json['grade']
        markov_score = 0.4 if 'markov_score' not in request.json else float(request.json['markov_score'])
        us_score = 0.3 if 'us_score' not in request.json else float(request.json['us_score'])
        ps_score = 0.4 if 'ps_score' not in request.json else float(request.json['ps_score'])
        mp_score = 0.4 if 'mp_score' not in request.json else float(request.json['mp_score'])
    except:
        return abort(500, 'missing argument/s in body: uids, cCode, lCode. n is optional')
    
    try:
        preds = service.predict_mixed(uids, c_code, l_code, n, score_above=score_above, grade=grades,
                                      markov_per=markov_score, us_per=us_score, ps_per=ps_score, mp_per=mp_score)
        return jsonify(preds)
    except Exception as e:
        logger.error(e)
        return abort(500, 'Error')

if __name__ == "__main__":
    app.run(debug=True, port=5000)