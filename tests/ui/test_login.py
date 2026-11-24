import pytest

from data.test_data import PASSWORD, ErrorMessages, Users

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_successful_login_opens_products_page(login_page):
    inventory = login_page.login_as(Users.STANDARD, PASSWORD)

    assert inventory.title == "Products"
    assert inventory.current_url.endswith("/inventory.html")


@pytest.mark.parametrize(
    ("username", "password", "expected_error"),
    [
        pytest.param(Users.STANDARD, "yanlis_sifre", ErrorMessages.WRONG_CREDENTIALS, id="yanlis-sifre"),
        pytest.param("olmayan_kullanici", PASSWORD, ErrorMessages.WRONG_CREDENTIALS, id="olmayan-kullanici"),
        pytest.param(Users.LOCKED_OUT, PASSWORD, ErrorMessages.LOCKED_OUT, id="kilitli-kullanici"),
        pytest.param("", PASSWORD, ErrorMessages.USERNAME_REQUIRED, id="bos-kullanici-adi"),
        pytest.param(Users.STANDARD, "", ErrorMessages.PASSWORD_REQUIRED, id="bos-sifre"),
    ],
)
def test_login_fails_with_invalid_credentials(login_page, username, password, expected_error):
    login_page.login(username, password)

    assert login_page.error_message == expected_error
    assert "inventory" not in login_page.current_url


def test_logout_returns_to_login_page(inventory_page, login_page):
    inventory_page.logout()

    assert login_page.is_displayed()


def test_products_page_requires_login(driver, login_page):
    """Giriş yapmadan ürünler sayfasına doğrudan gitmek engellenmeli."""
    from pages import InventoryPage

    InventoryPage(driver).open()

    assert login_page.is_displayed()
    assert "You can only access '/inventory.html' when you are logged in" in login_page.error_message
