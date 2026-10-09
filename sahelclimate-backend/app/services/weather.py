import urllib.request
import json
from typing import Dict, Any

class WeatherService:
    """
    Service de récupération des métriques météorologiques en temps réel via Open-Meteo API.
    """

    @staticmethod
    def get_current_weather(latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Interroge Open-Meteo pour récupérer la température, précipitations et vent en temps réel.
        En cas d'absence de réseau, bascule sur une estimation sahélienne réaliste.
        """
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}&"
            f"current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&"
            f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum&"
            f"timezone=auto"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SahelClimate/1.0"})
            with urllib.request.urlopen(req, timeout=4) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    current = data.get("current", {})
                    daily = data.get("daily", {})
                    
                    temp_mean = current.get("temperature_2m", 32.0)
                    temp_max = daily.get("temperature_2m_max", [temp_mean + 5])[0]
                    temp_min = daily.get("temperature_2m_min", [temp_mean - 5])[0]
                    rain_mm = daily.get("precipitation_sum", [current.get("precipitation", 0.0)])[0]
                    humidity = current.get("relative_humidity_2m", 40.0)
                    wind = current.get("wind_speed_10m", 12.0)

                    return {
                        "source": "Open-Meteo Live API",
                        "temp_mean": float(temp_mean),
                        "temp_max": float(temp_max),
                        "temp_min": float(temp_min),
                        "humidity_mean": float(humidity),
                        "wind_speed": float(wind),
                        "rain_mm": float(rain_mm)
                    }
        except Exception:
            pass

        # Fallback sahélien réaliste
        return {
            "source": "SahelClimate Weather Estimator (Fallback)",
            "temp_mean": 33.5,
            "temp_max": 39.0,
            "temp_min": 26.0,
            "humidity_mean": 35.0,
            "wind_speed": 14.5,
            "rain_mm": 0.0
        }
