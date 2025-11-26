# app.py
from flask import Flask, render_template, jsonify, request
from models import is_house_placeable

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
    length = float(data['length'])
    width = float(data['width'])
    rotation = float(data.get('rotation', 0))

    # ✅ Используем НОВУЮ функцию
    allowed, reason = is_house_placeable(lat, lon, length, width, rotation, building_type)

    return jsonify({
        'allowed': allowed,
        'reason': reason
    })

if __name__ == '__main__':
    app.run(debug=True)