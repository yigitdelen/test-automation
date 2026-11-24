import pytest

from config.settings import settings

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_api_health_check(client):
    response = client.ping()

    assert response.status_code == 201


@pytest.mark.smoke
def test_create_token_with_valid_credentials(client):
    response = client.create_token(settings.api_username, settings.api_password)

    assert response.status_code == 200
    token = response.json().get("token")
    assert isinstance(token, str) and token


@pytest.mark.parametrize(
    ("username", "password"),
    [
        pytest.param(settings.api_username, "yanlis_sifre", id="yanlis-sifre"),
        pytest.param("yanlis_kullanici", settings.api_password, id="yanlis-kullanici"),
        pytest.param("", "", id="bos-bilgiler"),
    ],
)
def test_create_token_with_invalid_credentials(client, username, password):
    response = client.create_token(username, password)

    # Not: Bu API hatalı girişte bile 200 döndürüyor; hatayı gövdedeki "reason" alanından anlıyoruz.
    assert response.status_code == 200
    assert response.json() == {"reason": "Bad credentials"}
