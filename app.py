import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = '4b72b99594c21823da17d783b2ea8b97'  # Ganti dengan API key Anda https://home.openweathermap.org/api_keys

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/location', methods=['POST'])
def get_location():
    data = request.get_json()
    latitude = data['latitude']
    longitude = data['longitude']

    # Panggil OpenWeatherMap Forecast API untuk mendapatkan ramalan cuaca 5 hari / 3 jam
    weather_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&units=metric&appid={API_KEY}'
    response = requests.get(weather_url)
    weather_data = response.json()

    if response.status_code == 200:
        if 'list' in weather_data:
            forecasts = []
            for forecast in weather_data['list']:
                forecast_data = {
                    'date': forecast['dt_txt'],
                    'temperature': forecast['main']['temp'],
                    'weather': forecast['weather'][0]['main'],
                    'description': forecast['weather'][0]['description']
                }
                forecasts.append(forecast_data)
            return jsonify({
                "status": "success",
                "latitude": latitude,
                "longitude": longitude,
                "forecasts": forecasts
            })
        else:
            error_message = "Forecast data not found in API response"
            return jsonify({"status": "error", "message": error_message}), 500
    else:
        error_message = "Unable to get weather forecast data"
        return jsonify({"status": "error", "message": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
