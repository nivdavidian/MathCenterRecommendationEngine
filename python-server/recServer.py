import dbAPI
import datetime
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import service

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes and origins

@app.route("/getpages")
def get_pages():
    try:
        try:
            term = request.args.get("term", "", type=str)
        except:
            term = ""
        results = dbAPI.get_recommend_search(term)
        worksheets = []
        for row in results:
            worksheet = {"worksheet_name": row[1], "worksheet_id": row[0]}
            worksheets.append(worksheet)
    except Exception as e:
        app.logger.error(f"get Pages:\n{e}")
        return abort(500, "Error")
    
    return jsonify(worksheets)

@app.route("/getpage")
def get_page():
    try:
        search = request.args.get("search")
        if search == None:
            return jsonify([])
        pages = dbAPI.get_page(search)
        worksheets = []
        for row in pages:
            worksheet = {"worksheet_name": row[1], "worksheet_id": row[0]}
            worksheets.append(worksheet)
    except Exception as e:
        app.logger.error(e)
        return abort(500, "Error")
    
    return jsonify(worksheets)
    
        
    
@app.route("/getrecommendation")
def get_recommendation():
    t = datetime.datetime.now()
    try:
        worksheet_uid = request.args.get("worksheet_uid")
        rec = service.recommend(worksheet_uid)
    except Exception as e:
        app.logger.error(e)
        return abort(500, "Error")
    
    app.logger.debug(f"recommend lag: {datetime.datetime.now()-t}")
    return jsonify(rec)
        


if __name__ == "__main__":
    app.run(debug=True, port=5000)