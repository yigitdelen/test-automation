"""API'nin hatalı veriye karşı nasıl davrandığı (girdi doğrulama).

İyi bir API hatalı isteği reddetmeli ve 400 Bad Request döndürmelidir.
restful-booker bu konuda ciddi hatalar içeriyor: eksik alanlarda sunucu çöküyor (500),
geçersiz verileri ise sessizce kaydediyor. Bu hatalar `xfail` olarak belgelendi;
testler *olması gereken* davranışı kontrol ediyor.
"""

import allure
import pytest

from data.test_data import new_booking

pytestmark = [pytest.mark.api, allure.parent_suite("API"), allure.suite("Girdi doğrulama")]

REQUIRED_FIELDS = ["firstname", "lastname", "totalprice", "depositpaid", "bookingdates"]


def test_invalid_json_is_rejected(client):
    response = client.create_booking_raw("{bu gecerli bir json degil")

    assert response.status_code == 400


@pytest.mark.known_bug
@pytest.mark.xfail(reason="HATA: Zorunlu alan eksik olunca API 400 yerine 500 (sunucu hatası) döndürüyor")
@pytest.mark.parametrize("missing_field", REQUIRED_FIELDS)
def test_missing_required_field_is_rejected(client, missing_field):
    payload = new_booking()
    del payload[missing_field]

    response = client.create_booking(payload)

    assert response.status_code == 400


@pytest.mark.known_bug
@pytest.mark.xfail(reason="HATA: Boş gövde gönderilince API 400 yerine 500 döndürüyor")
def test_empty_body_is_rejected(client):
    response = client.create_booking({})

    assert response.status_code == 400


@pytest.mark.known_bug
@pytest.mark.xfail(reason="HATA: API geçersiz veriyi reddetmiyor, 200 ile kaydediyor")
@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"totalprice": "abc"}, id="fiyat-metin"),
        pytest.param({"totalprice": -100}, id="fiyat-negatif"),
        pytest.param({"bookingdates": {"checkin": "abc", "checkout": "2027-01-01"}}, id="tarih-gecersiz"),
        pytest.param(
            {"bookingdates": {"checkin": "2027-01-10", "checkout": "2027-01-01"}},
            id="cikis-giristen-once",
        ),
    ],
)
def test_invalid_data_is_rejected(client, cleanup, overrides):
    response = client.create_booking(new_booking(**overrides))

    if response.status_code == 200:  # hata yüzünden kayıt oluştuysa temizle
        cleanup.append(response.json()["bookingid"])
    assert response.status_code == 400
