"""Rezervasyon CRUD (oluştur, oku, güncelle, sil) ve yetki testleri."""

import allure
import pytest
from jsonschema import validate

from api.schemas import BOOKING_IDS_SCHEMA, BOOKING_SCHEMA, CREATE_BOOKING_SCHEMA
from config.settings import settings
from data.test_data import new_booking

pytestmark = [pytest.mark.api, allure.parent_suite("API"), allure.suite("Rezervasyon")]


# --- Oluşturma (POST) ---------------------------------------------------------


@pytest.mark.smoke
def test_create_booking(client, cleanup):
    payload = new_booking()

    response = client.create_booking(payload)

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    body = response.json()
    cleanup.append(body["bookingid"])
    validate(instance=body, schema=CREATE_BOOKING_SCHEMA)
    assert body["booking"] == payload


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"firstname": "Yiğit", "lastname": "Çağlar-Şükrü Öztürk"}, id="turkce-karakterler"),
        pytest.param({"additionalneeds": "Kahvaltı 🍳 + geç çıkış"}, id="emoji"),
        pytest.param({"totalprice": 0}, id="ucretsiz"),
        pytest.param({"totalprice": 1_000_000}, id="yuksek-fiyat"),
        pytest.param({"depositpaid": False}, id="kapora-odenmedi"),
        pytest.param({"firstname": "A" * 100}, id="uzun-isim"),
        pytest.param({"bookingdates": {"checkin": "2027-01-01", "checkout": "2027-01-02"}}, id="tek-gece"),
    ],
)
def test_create_booking_with_various_valid_data(client, cleanup, overrides):
    """Veri odaklı test: aynı test farklı geçerli verilerle tekrar tekrar çalışır."""
    payload = new_booking(**overrides)

    response = client.create_booking(payload)

    assert response.status_code == 200
    cleanup.append(response.json()["bookingid"])
    assert response.json()["booking"] == payload
    # Kaydedilen veri, okunduğunda da aynı olmalı
    assert client.get_booking(response.json()["bookingid"]).json() == payload


def test_create_booking_without_optional_field(client, cleanup):
    payload = new_booking()
    del payload["additionalneeds"]

    response = client.create_booking(payload)

    assert response.status_code == 200
    cleanup.append(response.json()["bookingid"])
    assert response.json()["booking"] == payload


def test_create_booking_responds_fast_enough(client, cleanup):
    response = client.create_booking(new_booking())

    cleanup.append(response.json()["bookingid"])
    elapsed = response.elapsed.total_seconds()
    assert elapsed < settings.api_max_response_time, f"Cevap {elapsed:.2f} sn sürdü"


# --- Okuma (GET) ----------------------------------------------------------------


def test_get_booking_returns_created_data(client, created_booking):
    response = client.get_booking(created_booking["id"])

    assert response.status_code == 200
    validate(instance=response.json(), schema=BOOKING_SCHEMA)
    assert response.json() == created_booking["data"]


def test_get_booking_ids_returns_list(client, created_booking):
    response = client.get_booking_ids()

    assert response.status_code == 200
    validate(instance=response.json(), schema=BOOKING_IDS_SCHEMA)
    assert created_booking["id"] in [item["bookingid"] for item in response.json()]


@pytest.mark.parametrize(
    "booking_id",
    [
        pytest.param(999_999_999, id="olmayan-id"),
        pytest.param("abc", id="metin-id"),
        pytest.param(-1, id="negatif-id"),
    ],
)
def test_get_nonexistent_booking_returns_404(client, booking_id):
    response = client.get_booking(booking_id)

    assert response.status_code == 404


# --- Güncelleme (PUT / PATCH) ---------------------------------------------------


@pytest.mark.smoke
def test_update_booking_with_token(client, token, created_booking):
    updated = new_booking()

    response = client.update_booking(created_booking["id"], updated, token=token)

    assert response.status_code == 200
    assert response.json() == updated
    # Değişikliğin gerçekten kaydedildiğini ayrı bir GET ile doğrula
    assert client.get_booking(created_booking["id"]).json() == updated


def test_update_booking_with_basic_auth(client, created_booking):
    """API, token yerine kullanıcı adı/şifre (Basic Auth) ile yetkilendirmeyi de destekliyor."""
    updated = new_booking()

    response = client.update_booking(
        created_booking["id"], updated, basic_auth=(settings.api_username, settings.api_password)
    )

    assert response.status_code == 200
    assert response.json() == updated


@pytest.mark.parametrize(
    "fields",
    [
        pytest.param({"firstname": "Yeni"}, id="sadece-isim"),
        pytest.param({"totalprice": 999, "depositpaid": True}, id="fiyat-ve-kapora"),
        pytest.param({"bookingdates": {"checkin": "2027-03-01", "checkout": "2027-03-10"}}, id="tarihler"),
    ],
)
def test_partial_update_changes_only_given_fields(client, token, created_booking, fields):
    response = client.partial_update_booking(created_booking["id"], fields, token=token)

    assert response.status_code == 200
    assert response.json() == {**created_booking["data"], **fields}


def test_update_nonexistent_booking(client, token):
    response = client.update_booking(999_999_999, new_booking(), token=token)

    # Not: Bu API olmayan kayıtta 404 yerine 405 (Method Not Allowed) döndürüyor.
    assert response.status_code == 405


# --- Yetki kontrolleri (negatif testler) ----------------------------------------


@pytest.mark.parametrize(
    "auth",
    [
        pytest.param({}, id="yetki-yok"),
        pytest.param({"token": "gecersiz-token"}, id="gecersiz-token"),
        pytest.param({"basic_auth": ("admin", "yanlis_sifre")}, id="yanlis-basic-auth"),
    ],
)
def test_update_booking_without_valid_auth_is_forbidden(client, created_booking, auth):
    response = client.update_booking(created_booking["id"], new_booking(), **auth)

    assert response.status_code == 403
    # Kayıt değişmemiş olmalı
    assert client.get_booking(created_booking["id"]).json() == created_booking["data"]


@pytest.mark.parametrize(
    "auth",
    [pytest.param({}, id="yetki-yok"), pytest.param({"token": "gecersiz-token"}, id="gecersiz-token")],
)
def test_partial_update_without_valid_auth_is_forbidden(client, created_booking, auth):
    response = client.partial_update_booking(created_booking["id"], {"firstname": "Hacker"}, **auth)

    assert response.status_code == 403
    assert client.get_booking(created_booking["id"]).json() == created_booking["data"]


@pytest.mark.parametrize(
    "auth",
    [pytest.param({}, id="yetki-yok"), pytest.param({"token": "gecersiz-token"}, id="gecersiz-token")],
)
def test_delete_booking_without_valid_auth_is_forbidden(client, created_booking, auth):
    response = client.delete_booking(created_booking["id"], **auth)

    assert response.status_code == 403
    assert client.get_booking(created_booking["id"]).status_code == 200


# --- Silme (DELETE) -------------------------------------------------------------


@pytest.mark.smoke
def test_delete_booking(client, token, cleanup):
    booking_id = client.create_booking(new_booking()).json()["bookingid"]
    cleanup.append(booking_id)  # test ortada kalırsa yine de silinsin

    response = client.delete_booking(booking_id, token=token)

    # Not: Bu API başarılı silmede 201 döndürüyor (normalde 200 veya 204 beklenir).
    assert response.status_code == 201
    assert client.get_booking(booking_id).status_code == 404


def test_delete_already_deleted_booking(client, token):
    booking_id = client.create_booking(new_booking()).json()["bookingid"]
    client.delete_booking(booking_id, token=token)

    response = client.delete_booking(booking_id, token=token)

    # Not: Olmayan kaydı silmeye çalışınca 404 yerine 405 dönüyor.
    assert response.status_code == 405


# --- Uçtan uca akış -------------------------------------------------------------


def test_booking_full_lifecycle(client, token, cleanup):
    """Bir rezervasyonun tüm yaşam döngüsü: oluştur -> oku -> güncelle -> kısmi güncelle -> sil."""
    with allure.step("Oluştur"):
        payload = new_booking()
        booking_id = client.create_booking(payload).json()["bookingid"]
        cleanup.append(booking_id)  # test ortada kalırsa yine de silinsin

    with allure.step("Oku"):
        assert client.get_booking(booking_id).json() == payload

    with allure.step("Tamamen güncelle"):
        updated = new_booking()
        assert client.update_booking(booking_id, updated, token=token).json() == updated

    with allure.step("Kısmen güncelle"):
        patched = client.partial_update_booking(booking_id, {"additionalneeds": "Dinner"}, token=token)
        assert patched.json() == {**updated, "additionalneeds": "Dinner"}

    with allure.step("Sil ve silindiğini doğrula"):
        assert client.delete_booking(booking_id, token=token).status_code == 201
        assert client.get_booking(booking_id).status_code == 404
