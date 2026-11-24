"""GET /booking uç noktasının filtreleme özellikleri."""

import allure
import pytest

from data.test_data import new_booking

pytestmark = [pytest.mark.api, allure.parent_suite("API"), allure.suite("Filtreleme")]


def _ids(response) -> list[int]:
    assert response.status_code == 200
    return [item["bookingid"] for item in response.json()]


def test_filter_by_first_and_last_name(client, created_booking):
    data = created_booking["data"]

    ids = _ids(client.get_booking_ids(firstname=data["firstname"], lastname=data["lastname"]))

    assert ids == [created_booking["id"]], "Benzersiz soyadla yapılan aramada sadece bizim kaydımız dönmeli"


def test_filter_by_last_name_only(client, created_booking):
    ids = _ids(client.get_booking_ids(lastname=created_booking["data"]["lastname"]))

    assert created_booking["id"] in ids


def test_filter_with_no_match_returns_empty_list(client):
    ids = _ids(client.get_booking_ids(lastname="BoyleBirSoyadKesinlikleYok-123456"))

    assert ids == []


def test_filter_by_checkin_date(client, cleanup):
    """checkin filtresi, giriş tarihi verilen tarihten SONRA olan kayıtları döndürür."""
    payload = new_booking(bookingdates={"checkin": "2027-06-10", "checkout": "2027-06-15"})
    booking_id = client.create_booking(payload).json()["bookingid"]
    cleanup.append(booking_id)

    assert booking_id in _ids(client.get_booking_ids(checkin="2027-06-09"))
    assert booking_id not in _ids(client.get_booking_ids(checkin="2027-06-11"))
