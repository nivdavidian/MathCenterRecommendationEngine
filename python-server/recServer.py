import dbAPI
import service
import time
from flask import Flask, request, jsonify, abort, g, make_response
# from flask_cors import CORS

app = Flask(__name__)
# CORS(app)  # This enables CORS for all routes and origins

@app.before_request
def before_request():
    g.start_time = time.time()
    app.logger.info(f'content Length:{request.content_length}')
    
@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    app.logger.info(f"{request.path} took {duration}")
    return response

@app.route("/getpages")
def get_pages():
    try:
        term = request.args.get("term", "", type=str)
        c_code = request.args.get("cCode", "", type=str)
        l_code = request.args.get("lCode", "", type=str)
        print(request.args)
        results = dbAPI.get_recommend_search(term,l_code, c_code)
        worksheets = []
        for row in results:
            worksheet = {"worksheet_name": row[1], "worksheet_id": row[0]}
            worksheets.append(worksheet)
    except Exception as e:
        app.logger.error(f"get Pages:\n{e}")
        return abort(500, "Error")
    
    return jsonify(worksheets)

@app.route("/getclcodes")
def get_cl_codes():
    try:
        codes = dbAPI.get_distinct_cl_codes()
        
        cl_codes = {}
        for row in codes:
            c_code, l_code = row[0], row[1]
            arr = cl_codes.get(c_code, [])
            arr.append(l_code)
            cl_codes[c_code] = arr
            
        return jsonify(cl_codes)
    except Exception as e:
        app.logger.error(f"get cl codes:\n{e}")
        return abort(500, "Error")
    
        
    
@app.route("/getrecommendation")
def get_recommendation():
    try:
        worksheet_uid = request.args.get("worksheet_uid")
        c_code = request.args.get("cCode", "", type=str)
        l_code = request.args.get("lCode", "", type=str)
        rec = service.recommend(worksheet_uid, c_code=c_code, l_code=l_code)
        return jsonify(rec)
    except Exception as e:
        app.logger.error(e)
        return abort(500, "Error")
    
        
@app.route("/recuseralike", methods=["POST"])
def get_recommendation_user():
    try:
        already_watched = request.json["already_watched"]
        worksheet_uids = request.json["worksheet_uids"]
        c_code = request.json["cCode"]
        l_code = request.json["lCode"]
        rec = service.recommend_users_alike(already_watched, worksheet_uids, c_code=c_code, l_code=l_code)
        return jsonify(rec)
    except Exception as e:
        app.logger.error(e)
        return abort(500, "Error")
    
@app.route('/updaterecommendations', methods=['POST'])
def update_recommendations():
    try:
        service.update_files_recommendations(request.json)
        return make_response("OK", 200)
    except Exception as e:
        app.logger.error(e)
        return abort(500, "Error")
        
        
    

if __name__ == "__main__":
    app.run(debug=True, port=5000)