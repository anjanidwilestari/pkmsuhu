import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

API_KEY = '4b72b99594c21823da17d783b2ea8b97'  # Replace with your API key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/location', methods=['POST'])
def get_location():
    data = request.get_json()
    latitude = data['latitude']
    longitude = data['longitude']

    # Call OpenWeatherMap Current Weather API to get current weather
    current_weather_url = f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={API_KEY}'
    current_response = requests.get(current_weather_url)
    current_weather_data = current_response.json()

    if current_response.status_code == 200:
        # Get current weather information
        current_data = {
            'date': current_weather_data['dt'],
            'location': f"{current_weather_data['name']}, {current_weather_data['sys']['country']}",
            'temperature': current_weather_data['main']['temp'],
            'weather': current_weather_data['weather'][0]['main'],
            'description': current_weather_data['weather'][0]['description'],
            'icon': current_weather_data['weather'][0]['icon']
        }

        # Determine plant care based on temperature
        plant_care_info = get_plant_care_info(current_data['temperature'])

        # Call OpenWeatherMap Forecast API to get 5-day / 3-hour forecast
        forecast_weather_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&units=metric&appid={API_KEY}'
        forecast_response = requests.get(forecast_weather_url)
        forecast_weather_data = forecast_response.json()

        if forecast_response.status_code == 200:
            # Organize forecast data into a dictionary keyed by date
            forecasts = {}
            for forecast in forecast_weather_data['list']:
                date = forecast['dt_txt'].split()[0]
                if date not in forecasts:
                    forecasts[date] = []
                forecasts[date].append({
                    'time': forecast['dt'],
                    'temperature': forecast['main']['temp'],
                    'weather': forecast['weather'][0]['main'],
                    'description': forecast['weather'][0]['description'],
                    'icon': forecast['weather'][0]['icon']
                })

            return jsonify({
                "status": "success",
                "current": current_data,
                "forecasts": forecasts,
                "plant_care_info": plant_care_info
            })
        else:
            error_message = f"Unable to get forecast weather data. Error code {forecast_weather_data['cod']}: {forecast_weather_data['message']}"
            return jsonify({"status": "error", "message": error_message}), 500
    else:
        error_message = f"Unable to get current weather data. Error code {current_weather_data['cod']}: {current_weather_data['message']}"
        return jsonify({"status": "error", "message": error_message}), 500

def get_plant_care_info(temperature):
    if temperature < 15:
        return {
            'category': 'Suhu Dingin (di bawah 15°C)',
            'info': [
                'Lakukan penyiraman air setiap 7-10 hari.',
                'Berikan pupuk sekitar 5-10 kg per pohon dalam 2-3 bulan.'
            ]
        }
    elif 15 <= temperature < 25:
        return {
            'category': 'Suhu Optimal (sekitar 15-25°C)',
            'info': [
                'Lakukan penyiraman air setiap 5-7 hari.',
                'Berikan pupuk sekitar 200-300 gram per pohon dalam 1-2 bulan.'
            ]
        }
    else:
        return {
            'category': 'Suhu Panas (di atas 25°C)',
            'info': [
                'Lakukan penyiraman air setiap 2-4 hari.',
                'Berikan pupuk sekitar 300-500 gram per pohon dalam 1 bulan.'
            ]
        }

@app.route('/predict')
def predict():
    return render_template('predict.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/coba')
def coba():
    return render_template('coba-widget.html')

if __name__ == '__main__':
    app.run(debug=True)
