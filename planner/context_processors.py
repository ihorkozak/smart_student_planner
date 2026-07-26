import requests
from django.conf import settings

def weather_processor(request):
    if not request.user.is_authenticated:
        return {}

    try:
        ip_response = requests.get('http://ip-api.com/json/', timeout=3)
        ip_data = ip_response.json()
        city = ip_data.get('city', 'Vienna')

        url = "https://api.openweathermap.org/data/2.5/weather"
        response = requests.get(url, params={
            'q': city,
            'appid': settings.OPENWEATHER_API_KEY,
            'units': 'metric'
        }, timeout=3)
        data = response.json()
        weather = {
            'city': city,
            'temperature': round(data['main']['temp']),
            'condition': data['weather'][0]['description'],
        }
    except:
        weather = None

    return {'weather': weather}