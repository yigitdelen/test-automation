import pytest
from jsonschema import validate

from api.schemas import BOOKING_IDS_SCHEMA, BOOKING_SCHEMA, CREATE_BOOKING_SCHEMA
from data.test_data import new_booking

pytestmark = pytest.mark.api


# --- Oluşturma (POST) ---------------------------------------------------------

@pytest.mark.smoke
def test_create_booking(client, token):
    payload = new_booking()

    response = client.create_booking(payload)

    assert response.status_code == 200
    body = response.json()
    validate(instance=body, schema=CREATE_BOOKING_SCHEMA)
    assert body["booking"] == payload

    client.delete_booking(body["bookingid"], token=token)


# --- Okuma (GET) ----------------------------------------------------------------

def test_get_booking_returns_created_data(client, created_booking):
    response = client.get_booking(created_booking["id"])

    assert response.status_code == 200
    validate(instance=response.json(), schema=BOOKING_SCHEMA)
    assert response.json() == created_booking["data"]


def test_get_booking_ids_returns_list(client):
    response = client.get_booking_ids()

    assert response.status_code == 200
    validate(instance=response.json(), schema=BOOKING_IDS_SCHEMA)
    assert len(response.json()) > 0


def test_filter_bookings_by_name(client, created_booking):
    data = created_booking["data"]

    response = client.get_booking_ids(firstname=data["firstname"], lastname=data["lastname"])

    assert response.status_code == 200
    ids = [item["bookingid"] for item in response.json()]
    assert created_booking["id"] in ids


def test_get_nonexistent_booking_returns_404(client):
    response = client.get_booking(999_999_999)

    assert response.status_code == 404


# --- Güncelleme (PUT / PATCH) ---------------------------------------------------

def test_update_booking_with_token(client, token, created_booking):
    updated = new_booking(firstname="Guncellendi", totalprice=2000, depositpaid=False)

    response = client.update_booking(created_booking["id"], updated, token=token)

    assert response.status_code == 200
    assert response.json() == updated
    # Değişikliğin gerçekten kaydedildiğini ayrı bir GET ile doğrula
    assert client.get_booking(created_booking["id"]).json() == updated


def test_partial_update_booking(client, token, created_booking):
    response = client.partial_update_booking(
        created_booking["id"], {"firstname": "Yeni", "additionalneeds": "Dinner"}, token=token
    )

    assert response.status_code == 200
    expected = {**created_booking["data"], "firstname": "Yeni", "additionalneeds": "Dinner"}
    assert response.json() == expected


# --- Yetki kontrolleri (negatif testler) ----------------------------------------

@pytest.mark.parametrize(
    "bad_token",
    [pytest.param(None, id="token-yok"), pytest.param("gecersiz-token", id="gecersiz-token")],
)
def test_update_booking_without_valid_token_is_forbidden(client, created_booking, bad_token):
    response = client.update_booking(created_booking["id"], new_booking(), token=bad_token)

    assert response.status_code == 403
    # Kayıt değişmemiş olmalı
    assert client.get_booking(created_booking["id"]).json() == created_booking["data"]


def test_delete_booking_without_token_is_forbidden(client, created_booking):
    response = client.delete_booking(created_booking["id"])

    assert response.status_code == 403
    assert client.get_booking(created_booking["id"]).status_code == 200


# --- Silme (DELETE) -------------------------------------------------------------

@pytest.mark.smoke
def test_delete_booking(client, token):
    booking_id = client.create_booking(new_booking()).json()["bookingid"]

    response = client.delete_booking(booking_id, token=token)

    # Not: Bu API başarılı silmede 201 döndürüyor (normalde 200 veya 204 beklenir).
    assert response.status_code == 201
    assert client.get_booking(booking_id).status_code == 404
