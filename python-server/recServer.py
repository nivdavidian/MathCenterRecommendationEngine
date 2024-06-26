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
    
        
    
@app.route("/api/getrecommendation")
def get_recommendation():
    try:
        worksheet_uid = request.args.get("worksheet_uid")
        c_code = request.args.get("cCode", "", type=str)
        l_code = request.args.get("lCode", "", type=str)
        rec = service.recommend(worksheet_uid, c_code=c_code, l_code=l_code)
        return jsonify(rec)
    except Exception as e:
        logger.error(e)
        return abort(500, "Error")
    
        
@app.route("/api/recuseralike", methods=["POST"])
def get_recommendation_user():
    try:
        already_watched = request.json["already_watched"]
        worksheet_uids = request.json["worksheet_uids"]
        c_code = request.json["cCode"]
        l_code = request.json["lCode"]
        rec = service.recommend_users_alike(already_watched, worksheet_uids, c_code=c_code, l_code=l_code)
        rec = service.get_worksheets_info(rec, c_code, l_code)
        rec = list(rec.values())
        return jsonify(rec)
    except Exception as e:
        logger.error(e)
        return abort(500, "Error")
    
@app.route('/api/updaterecommendations', methods=['POST'])
def update_recommendations():
    try:
        service.update_files_recommendations(request.json)
        return make_response("OK", 200)
    except Exception as e:
        logger.error(e)
        return abort(500, "Error")

@app.route('/api/mostpopular', methods=['POST'])
def most_popular():
    try:
        populars = service.most_popular_in_month(**request.json)
        res_info = service.get_worksheets_info(populars, request.json['cCode'], request.json['lCode'])
        res_info = [res_info[uid] for uid in populars]
        return jsonify(res_info)
    except Exception as e:
        logger.error(e)
        return abort(500, "Error")
    
@app.route('/api/markov', methods=['POST'])
def markov():
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
        

if __name__ == "__main__":
    app.run(debug=True, port=5000)