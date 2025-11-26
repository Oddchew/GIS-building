# app.py
from flask import Flask, render_template, jsonify, request
from models import is_allowed_to_build

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_location():
    data = request.json
    lat = float(data['lat'])
    lon = float(data['lng'])
    building_type = data['building_type']
    size = float(data['size'])

    allowed, reason = is_allowed_to_build(lat, lon, building_type, size)

    return jsonify({
        'allowed': allowed,
        'reason': reason
    })

if __name__ == '__main__':
    app.run(debug=True)