import allure
import pytest

from config.settings import settings

pytestmark = [pytest.mark.api, allure.parent_suite("API"), allure.suite("Kimlik doğrulama")]


@pytest.mark.smoke
def test_api_health_check(client):
    response = client.ping()

    assert response.status_code == 201


@pytest.mark.smoke
def test_create_token_with_valid_credentials(client):
    response = client.create_token(settings.api_username, settings.api_password)

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")
    token = response.json().get("token")
    assert isinstance(token, str)
    assert token


def test_each_login_returns_a_new_token(client):
    first = client.create_token(settings.api_username, settings.api_password).json()["token"]
    second = client.create_token(settings.api_username, settings.api_password).json()["token"]

    assert first != second


@pytest.mark.parametrize(
    ("username", "password"),
    [
        pytest.param(settings.api_username, "yanlis_sifre", id="yanlis-sifre"),
        pytest.param("yanlis_kullanici", settings.api_password, id="yanlis-kullanici"),
        pytest.param(settings.api_username.upper(), settings.api_password, id="buyuk-harf"),
        pytest.param("", "", id="bos-bilgiler"),
    ],
)
def test_create_token_with_invalid_credentials(client, username, password):
    response = client.create_token(username, password)

    # Not: Bu API hatalı girişte bile 200 döndürüyor (normalde 401 beklenir);
    # hatayı gövdedeki "reason" alanından anlıyoruz.
    assert response.status_code == 200
    assert response.json() == {"reason": "Bad credentials"}
