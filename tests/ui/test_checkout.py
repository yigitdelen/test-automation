import allure
import pytest

from data.test_data import TAX_RATE, ErrorMessages, Products, new_customer

pytestmark = [pytest.mark.ui, allure.parent_suite("Web UI"), allure.suite("Ödeme")]


@pytest.mark.smoke
def test_complete_purchase_end_to_end(inventory_page):
    """Uçtan uca satın alma: sepete ekle -> sepeti kontrol et -> bilgileri gir -> tutarı doğrula -> bitir."""
    products = [Products.BACKPACK, Products.BOLT_TSHIRT]
    for product in products:
        inventory_page.add_to_cart(product)

    cart = inventory_page.header.go_to_cart()
    assert sorted(cart.item_names()) == sorted(products)

    overview = cart.checkout().continue_to_overview(**new_customer())
    assert sorted(overview.item_names()) == sorted(products)

    complete = overview.finish()
    assert complete.message == "Thank you for your order!"
    # Sipariş sonrası sepet boşalmalı
    assert complete.header.cart_count() == 0


@pytest.mark.parametrize(
    "products",
    [
        pytest.param([Products.ONESIE], id="tek-urun"),
        pytest.param([Products.BACKPACK, Products.BIKE_LIGHT, Products.FLEECE_JACKET], id="uc-urun"),
        pytest.param(list(Products.ALL), id="tum-urunler"),
    ],
)
def test_order_totals_are_calculated_correctly(inventory_page, products):
    """Ara toplam = fiyatların toplamı, vergi = ara toplamın %8'i, genel toplam = ara toplam + vergi."""
    for product in products:
        inventory_page.add_to_cart(product)

    overview = inventory_page.header.go_to_cart().checkout().continue_to_overview(**new_customer())

    prices = overview.item_prices()
    assert len(prices) == len(products)
    assert overview.subtotal == pytest.approx(sum(prices))
    assert overview.tax == pytest.approx(round(overview.subtotal * TAX_RATE, 2))
    assert overview.total == pytest.approx(overview.subtotal + overview.tax)


@pytest.mark.parametrize(
    ("field", "expected_error"),
    [
        pytest.param("first_name", ErrorMessages.FIRST_NAME_REQUIRED, id="ad-bos"),
        pytest.param("last_name", ErrorMessages.LAST_NAME_REQUIRED, id="soyad-bos"),
        pytest.param("postal_code", ErrorMessages.POSTAL_CODE_REQUIRED, id="posta-kodu-bos"),
    ],
)
def test_checkout_form_requires_all_fields(inventory_page, field, expected_error):
    inventory_page.add_to_cart(Products.BACKPACK)
    info_page = inventory_page.header.go_to_cart().checkout()
    customer = {**new_customer(), field: ""}

    info_page.fill_form(**customer)

    assert info_page.error_message == expected_error
    assert info_page.current_url.endswith(info_page.PATH), "Hata varken bir sonraki adıma geçilmemeli"


def test_cancel_on_information_step_returns_to_cart(inventory_page):
    inventory_page.add_to_cart(Products.BACKPACK)
    info_page = inventory_page.header.go_to_cart().checkout()

    cart = info_page.cancel()

    assert cart.item_names() == [Products.BACKPACK]


def test_cancel_on_overview_step_keeps_cart(inventory_page):
    inventory_page.add_to_cart(Products.BACKPACK)
    overview = inventory_page.header.go_to_cart().checkout().continue_to_overview(**new_customer())

    inventory = overview.cancel()

    assert inventory.header.cart_count() == 1


def test_back_home_after_order(inventory_page):
    inventory_page.add_to_cart(Products.ONESIE)
    complete = inventory_page.header.go_to_cart().checkout().continue_to_overview(**new_customer()).finish()

    inventory = complete.back_home()

    assert inventory.title == "Products"
    assert inventory.header.cart_count() == 0
