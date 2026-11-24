import pytest

from api.booking_client import BookingClient
from config.settings import settings
from data.test_data import new_booking


@pytest.fixture(scope="session")
def client() -> BookingClient:
    return BookingClient()


@pytest.fixture(scope="session")
def token(client) -> str:
    response = client.create_token(settings.api_username, settings.api_password)
    assert response.status_code == 200, f"Token alınamadı: {response.text}"
    return response.json()["token"]


@pytest.fixture
def created_booking(client, token) -> dict:
    """Test için yeni bir rezervasyon oluşturur, test bitince siler (temizlik).

    Döndürdüğü sözlük: {"id": ..., "data": <gönderilen veri>}
    """
    payload = new_booking()
    response = client.create_booking(payload)
    assert response.status_code == 200, f"Rezervasyon oluşturulamadı: {response.text}"
    booking = {"id": response.json()["bookingid"], "data": payload}

    yield booking

    client.delete_booking(booking["id"], token=token)
