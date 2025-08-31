from flask import Blueprint, render_template
import requests
from flask import request, jsonify

OPENWEATHER_API_KEY =  "a6cfac316dc3684564ad11d0ac21b1f8" #"3044df3caf1c2b431c1a7fc48c4875ab"  "a6cfac316dc3684564ad11d0ac21b1f8"
weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/weather')
def weather_page():
    return render_template('weather.html')

@weather_bp.route('/api/weather', methods=['POST'])
def get_weather():
    try:
        data = request.get_json()
        print("Received data:", data)

        if not data:
            return jsonify({'error': 'No data received'}), 400

        lat = data.get('lat')
        lon = data.get('lon')

        if not lat or not lon:
            return jsonify({'error': 'Missing location data'}), 400

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={a6cfac316dc3684564ad11d0ac21b1f8}&units=metric"
        response = requests.get(url)
        weather_data = response.json()

        print("Weather API raw response:", weather_data)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch weather'}), 500

        return jsonify({
            'location': f"{weather_data['name']}, {weather_data['sys']['country']}",
            'weather': weather_data['weather'][0]['description'].capitalize(),
            'temp': round(weather_data['main']['temp'], 1),
            'humidity': weather_data['main']['humidity'],
            'wind_speed': weather_data['wind']['speed']
        })
    except Exception as e:
        print("Error in weather route:", str(e))
        return jsonify({'error': str(e)}), 500
