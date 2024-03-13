import dbAPI
import datetime
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import service

app = Flask(__name__)
# CORS(app)  # This enables CORS for all routes and origins

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
    t = datetime.datetime.now()
    try:
        worksheet_uid = request.args.get("worksheet_uid")
        c_code = request.args.get("cCode", "", type=str)
        l_code = request.args.get("lCode", "", type=str)
        print(request.args)
        rec = service.recommend(worksheet_uid, c_code=c_code, l_code=l_code)
        app.logger.debug(f"recommend lag: {datetime.datetime.now()-t}")
        return jsonify(rec)
    except Exception as e:
        app.logger.error(e)
        return abort(500, "Error")
    
        


if __name__ == "__main__":
    app.run(debug=True, port=5000)