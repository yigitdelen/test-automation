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
def cleanup(client, token):
    """Test sırasında oluşturulan rezervasyonları test bitince siler.

    Kullanım: cleanup.append(booking_id)
    Test kalsa bile silme çalışır; paylaşılan demo API'de çöp kayıt bırakmayız.
    """
    booking_ids: list[int] = []
    yield booking_ids
    for booking_id in booking_ids:
        client.delete_booking(booking_id, token=token)


@pytest.fixture
def created_booking(client, cleanup) -> dict:
    """Test için hazır bir rezervasyon oluşturur.

    Döndürdüğü sözlük: {"id": ..., "data": <gönderilen veri>}
    """
    payload = new_booking()
    response = client.create_booking(payload)
    assert response.status_code == 200, f"Rezervasyon oluşturulamadı: {response.text}"
    booking_id = response.json()["bookingid"]
    cleanup.append(booking_id)
    return {"id": booking_id, "data": payload}
