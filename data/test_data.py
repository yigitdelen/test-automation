"""Testlerde kullanılan sabit veriler ve veri üreten yardımcılar."""

import uuid

# --- saucedemo.com ---------------------------------------------------------

PASSWORD = "secret_sauce"


class Users:
    STANDARD = "standard_user"
    LOCKED_OUT = "locked_out_user"


class Products:
    BACKPACK = "Sauce Labs Backpack"
    BIKE_LIGHT = "Sauce Labs Bike Light"
    BOLT_TSHIRT = "Sauce Labs Bolt T-Shirt"


class ErrorMessages:
    USERNAME_REQUIRED = "Epic sadface: Username is required"
    PASSWORD_REQUIRED = "Epic sadface: Password is required"
    WRONG_CREDENTIALS = "Epic sadface: Username and password do not match any user in this service"
    LOCKED_OUT = "Epic sadface: Sorry, this user has been locked out."
    FIRST_NAME_REQUIRED = "Error: First Name is required"
    LAST_NAME_REQUIRED = "Error: Last Name is required"
    POSTAL_CODE_REQUIRED = "Error: Postal Code is required"


CUSTOMER = {"first_name": "Yigit", "last_name": "Test", "postal_code": "34000"}


# --- restful-booker API ----------------------------------------------------

def new_booking(**overrides) -> dict:
    """Her çağrıda benzersiz soyadlı yeni bir rezervasyon verisi üretir.

    Benzersiz soyad sayesinde aynı API'yi kullanan başka kişilerin
    kayıtlarıyla karışmaz.
    """
    booking = {
        "firstname": "Yigit",
        "lastname": f"Test-{uuid.uuid4().hex[:8]}",
        "totalprice": 1500,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-12-01", "checkout": "2026-12-05"},
        "additionalneeds": "Breakfast",
    }
    booking.update(overrides)
    return booking
