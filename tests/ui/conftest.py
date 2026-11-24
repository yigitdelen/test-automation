import pytest

from data.test_data import PASSWORD, Users
from pages import InventoryPage, LoginPage


@pytest.fixture
def login_page(driver) -> LoginPage:
    return LoginPage(driver).open()


@pytest.fixture
def inventory_page(login_page) -> InventoryPage:
    """Giriş yapılmış hâlde ürünler sayfası (girişin kendisini test etmeyen testler için)."""
    return login_page.login_as(Users.STANDARD, PASSWORD)
