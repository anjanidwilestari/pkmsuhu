import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = '4b72b99594c21823da17d783b2ea8b97'  # Ganti dengan API key Anda

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/location', methods=['POST'])
def get_location():
    data = request.get_json()
    latitude = data['latitude']
    longitude = data['longitude']

    # Panggil OpenWeatherMap Current Weather API untuk mendapatkan cuaca saat ini
    current_weather_url = f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={API_KEY}'
    current_response = requests.get(current_weather_url)
    current_weather_data = current_response.json()

    if current_response.status_code == 200:
        # Ambil informasi cuaca saat ini
        current_data = {
            'date': current_weather_data['dt'],
            'location': current_weather_data['name'],
            'temperature': current_weather_data['main']['temp'],
            'weather': current_weather_data['weather'][0]['main'],
            'description': current_weather_data['weather'][0]['description']
        }

        # Panggil OpenWeatherMap Forecast API untuk mendapatkan ramalan cuaca 5 hari / 3 jam
        forecast_weather_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&units=metric&appid={API_KEY}'
        forecast_response = requests.get(forecast_weather_url)
        forecast_weather_data = forecast_response.json()

        if forecast_response.status_code == 200:
            # Ambil ramalan cuaca 5 hari ke depan dimulai dari hari setelah hari ini
            forecasts = []
            dates_seen = set()
            today_date = current_data['date']
            for forecast in forecast_weather_data['list']:
                # Ambil tanggal saja tanpa jam
                date = forecast['dt_txt'].split()[0]
                if date not in dates_seen and forecast['dt'] > today_date:
                    forecast_data = {
                        'date': forecast['dt'],
                        'temperature': forecast['main']['temp'],
                        'weather': forecast['weather'][0]['main'],
                        'description': forecast['weather'][0]['description']
                    }
                    forecasts.append(forecast_data)
                    dates_seen.add(date)
                    if len(forecasts) == 5:
                        break

            return jsonify({
                "status": "success",
                "current": current_data,
                "forecasts": forecasts
            })
        else:
            error_message = f"Unable to get forecast weather data. Error code {forecast_weather_data['cod']}: {forecast_weather_data['message']}"
            return jsonify({"status": "error", "message": error_message}), 500
    else:
        error_message = f"Unable to get current weather data. Error code {current_weather_data['cod']}: {current_weather_data['message']}"
        return jsonify({"status": "error", "message": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
