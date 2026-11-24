"""Testlerde kullanılan sabit veriler ve veri üreten yardımcılar.

Sabit veriler (kullanıcı adları, hata mesajları) burada tanımlanır.
Değişken veriler (müşteri adı, rezervasyon) Faker ile her çalıştırmada rastgele üretilir;
böylece testler tek bir veri setine "alışmaz" ve paylaşılan demo API'de kayıtlar çakışmaz.
"""

import random
import uuid
from datetime import date, timedelta

from faker import Faker

fake = Faker("tr_TR")  # Türkçe isimler: ğ, ü, ş, ı, ö, ç karakterleri de test edilmiş olur

# --- saucedemo.com ---------------------------------------------------------

PASSWORD = "secret_sauce"
TAX_RATE = 0.08  # sitenin uyguladığı vergi oranı


class Users:
    STANDARD = "standard_user"
    LOCKED_OUT = "locked_out_user"
    PROBLEM = "problem_user"
    PERFORMANCE_GLITCH = "performance_glitch_user"
    ERROR = "error_user"
    VISUAL = "visual_user"

    # Giriş yapabilen tüm kullanıcılar
    ALL_ACTIVE = (STANDARD, PROBLEM, PERFORMANCE_GLITCH, ERROR, VISUAL)


class Products:
    BACKPACK = "Sauce Labs Backpack"
    BIKE_LIGHT = "Sauce Labs Bike Light"
    BOLT_TSHIRT = "Sauce Labs Bolt T-Shirt"
    FLEECE_JACKET = "Sauce Labs Fleece Jacket"
    ONESIE = "Sauce Labs Onesie"
    RED_TSHIRT = "Test.allTheThings() T-Shirt (Red)"

    ALL = (BACKPACK, BIKE_LIGHT, BOLT_TSHIRT, FLEECE_JACKET, ONESIE, RED_TSHIRT)


class ErrorMessages:
    USERNAME_REQUIRED = "Epic sadface: Username is required"
    PASSWORD_REQUIRED = "Epic sadface: Password is required"
    WRONG_CREDENTIALS = "Epic sadface: Username and password do not match any user in this service"
    LOCKED_OUT = "Epic sadface: Sorry, this user has been locked out."
    LOGIN_REQUIRED = "Epic sadface: You can only access '/inventory.html' when you are logged in."
    FIRST_NAME_REQUIRED = "Error: First Name is required"
    LAST_NAME_REQUIRED = "Error: Last Name is required"
    POSTAL_CODE_REQUIRED = "Error: Postal Code is required"


def new_customer() -> dict:
    """Ödeme formu için rastgele müşteri bilgisi."""
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "postal_code": fake.postcode(),
    }


# --- restful-booker API ----------------------------------------------------


def new_booking(**overrides) -> dict:
    """Rastgele ama geçerli bir rezervasyon verisi üretir.

    Soyadın sonuna eklenen kısa benzersiz kod sayesinde aynı demo API'yi
    kullanan başka kişilerin kayıtlarıyla karışmaz.
    """
    checkin = date.today() + timedelta(days=random.randint(1, 60))
    checkout = checkin + timedelta(days=random.randint(1, 14))
    booking = {
        "firstname": fake.first_name(),
        "lastname": f"{fake.last_name()}-{uuid.uuid4().hex[:6]}",
        "totalprice": random.randint(100, 5000),
        "depositpaid": fake.boolean(),
        "bookingdates": {"checkin": checkin.isoformat(), "checkout": checkout.isoformat()},
        "additionalneeds": random.choice(["Breakfast", "Dinner", "Late checkout", "Airport transfer"]),
    }
    booking.update(overrides)
    return booking
