import pytest

from data.test_data import Users
from pages import InventoryPage, LoginPage


@pytest.fixture
def login_page(driver) -> LoginPage:
    return LoginPage(driver).open()


@pytest.fixture
def login_as(login_page):
    """Fabrika fixture: istenen kullanıcıyla hızlıca giriş yapar.

    Kullanım: inventory = login_as(Users.PROBLEM)
    """

    def _login(username: str) -> InventoryPage:
        return login_page.login_with_session_cookie(username)

    return _login


@pytest.fixture
def inventory_page(login_as) -> InventoryPage:
    """standard_user ile giriş yapılmış hâlde ürünler sayfası."""
    return login_as(Users.STANDARD)
