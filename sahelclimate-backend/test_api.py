import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_parcels():
    """Vérifie la récupération de la liste des parcelles"""
    response = client.get("/api/v1/parcels")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "location_name" in data[0]

def test_create_parcel():
    """Vérifie la création d'une parcelle et l'intégration Sentinel-2"""
    payload = {
        "location_name": "Parcelle Test Massakory",
        "crop_type": "Sésame",
        "growth_stage": "dev",
        "area_ha": 5.0,
        "latitude": 12.996,
        "longitude": 15.729
    }
    response = client.post("/api/v1/parcels", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["location_name"] == "Parcelle Test Massakory"
    assert "ndvi_value" in data
    assert "ndwi_value" in data

def test_water_balance():
    """Vérifie le moteur de calcul du bilan hydrique FAO-56"""
    payload = {
        "growth_stage": "mid",
        "temp_mean": 36.5,
        "temp_max": 42.0,
        "temp_min": 29.0,
        "humidity_mean": 20.0,
        "wind_speed": 3.8,
        "rain_mm": 0.0
    }
    response = client.post("/api/v1/parcels/1/water-balance", json=payload)
    assert response.status_code == 200
    data = response.json()
    analysis = data["water_balance_analysis"]
    assert "et0_daily_mm" in analysis
    assert "total_parcel_volume_m3" in analysis
    assert analysis["total_parcel_volume_m3"] > 0

def test_send_alert_sms():
    """Vérifie l'envoi d'une alerte par SMS"""
    payload = {"channel": "SMS"}
    response = client.post("/api/v1/parcels/1/send-alert", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DISPATCHED"
    assert data["dispatch_details"]["channel"] == "SMS"

def test_send_alert_whatsapp():
    """Vérifie l'envoi d'une alerte par WhatsApp"""
    payload = {"channel": "WhatsApp"}
    response = client.post("/api/v1/parcels/1/send-alert", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DISPATCHED"
    assert data["dispatch_details"]["channel"] == "WhatsApp"

def test_parcel_not_found():
    """Vérifie la gestion de l'erreur 404 pour une parcelle inexistante"""
    payload = {"channel": "SMS"}
    response = client.post("/api/v1/parcels/9999/send-alert", json=payload)
    assert response.status_code == 404



def test_dispatch_alert_endpoint():
    response = client.post(
        "/api/v1/alerts/dispatch-irrigation",
        json={
            "parcel_id": 1,
            "parcel_name": "Parcelle Test",
            "phone_number": "+23566000000",
            "water_deficit_mm": 4.5,
            "total_volume_m3": 112.5,
            "channel": "sms"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_export_excel():
    response = client.get("/api/v1/parcels/1/export/excel")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def test_export_pdf():
    response = client.get("/api/v1/parcels/1/export/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
