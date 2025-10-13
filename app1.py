from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import requests
load_dotenv()

app=Flask(__name__)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


@app.route('/')
def home():
    return render_template('location.html', api_key=GOOGLE_MAPS_API_KEY)
@app.route('/get_location', methods=['GET', 'POST'])
def get_location():
    data = request.get_json() 
    address = data.get('address')

    if not address:
        return jsonify({'error': 'Address is required'}), 400
    
    url = f"https://maps.googleapis.com/maps/api/geocode/json"

    params = {
         "address": address,
         "key": GOOGLE_MAPS_API_KEY
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result['status'] == 'OK':
        location = result['results'][0]['geometry']['location']
        return jsonify({
            'latitude': location['lat'],
            'longitude': location['lng']
        })
    else:
        return jsonify({'error': 'Unable to find location'}), 404
    

if __name__=="__main__":
    app.run(debug=True)

