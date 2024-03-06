import dbAPI
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

@app.route("/getpages")
def get_pages():
    try:
        page = int(request.args.get("page", 1))
        pages100 = dbAPI.get_worksheets_page(page)
        worksheets = []
        for row in pages100:
            worksheet = {"worksheet_name": row[0], "worksheet_id": row[1]}
            worksheets.append(worksheet)
    except Exception as e:
        app.logger.debug(f"get Pages:\n{e}")
        return abort(500, "Error")
    
    return jsonify(worksheets)

@app.route("/getrecommendation/<id>")
def get_recommendation(id):
    pass


if __name__ == "__main__":
    app.run(debug=True, port=5000)