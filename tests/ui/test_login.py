import allure
import pytest

from config.settings import settings
from data.test_data import PASSWORD, ErrorMessages, Users
from pages import InventoryPage

pytestmark = [pytest.mark.ui, allure.parent_suite("Web UI"), allure.suite("Giriş")]


@pytest.mark.smoke
def test_successful_login_opens_products_page(login_page):
    inventory = login_page.login_as(Users.STANDARD, PASSWORD)

    assert inventory.title == "Products"
    assert inventory.current_url.endswith("/inventory.html")


@pytest.mark.parametrize("username", Users.ALL_ACTIVE)
def test_all_active_users_can_log_in(login_page, username):
    """performance_glitch_user yavaş açılır; akıllı bekleme (explicit wait) sayesinde test yine geçer."""
    inventory = login_page.login_as(username, PASSWORD)

    assert inventory.title == "Products"


@pytest.mark.parametrize(
    ("username", "password", "expected_error"),
    [
        pytest.param(Users.STANDARD, "yanlis_sifre", ErrorMessages.WRONG_CREDENTIALS, id="yanlis-sifre"),
        pytest.param("olmayan_kullanici", PASSWORD, ErrorMessages.WRONG_CREDENTIALS, id="olmayan-kullanici"),
        pytest.param("STANDARD_USER", PASSWORD, ErrorMessages.WRONG_CREDENTIALS, id="buyuk-harf-duyarli"),
        pytest.param(Users.LOCKED_OUT, PASSWORD, ErrorMessages.LOCKED_OUT, id="kilitli-kullanici"),
        pytest.param("", PASSWORD, ErrorMessages.USERNAME_REQUIRED, id="bos-kullanici-adi"),
        pytest.param(Users.STANDARD, "", ErrorMessages.PASSWORD_REQUIRED, id="bos-sifre"),
        pytest.param("", "", ErrorMessages.USERNAME_REQUIRED, id="ikisi-de-bos"),
        pytest.param(
            "' OR '1'='1", "' OR '1'='1", ErrorMessages.WRONG_CREDENTIALS, id="sql-injection-denemesi"
        ),
    ],
)
def test_login_fails_with_invalid_credentials(login_page, username, password, expected_error):
    login_page.login(username, password)

    assert login_page.error_message == expected_error
    assert "inventory" not in login_page.current_url


def test_error_message_can_be_closed(login_page):
    login_page.login("", "")
    assert login_page.has_error()

    login_page.close_error()

    assert not login_page.has_error()


def test_password_field_is_masked(login_page):
    """Şifre ekranda açık metin olarak görünmemeli."""
    assert login_page.password_field_type() == "password"


def test_logout_returns_to_login_page(login_page):
    inventory = login_page.login_as(Users.STANDARD, PASSWORD)

    inventory.header.logout()

    assert login_page.is_displayed()


def test_cannot_access_products_after_logout(driver, login_page):
    inventory = login_page.login_as(Users.STANDARD, PASSWORD)
    inventory.header.logout()

    driver.get(f"{settings.base_url}/{InventoryPage.PATH}")

    assert login_page.is_displayed()
    assert login_page.error_message == ErrorMessages.LOGIN_REQUIRED


def test_products_page_requires_login(driver, login_page):
    """Giriş yapmadan ürünler sayfasına doğrudan gitmek engellenmeli."""
    driver.get(f"{settings.base_url}/{InventoryPage.PATH}")

    assert login_page.is_displayed()
    assert login_page.error_message == ErrorMessages.LOGIN_REQUIRED
