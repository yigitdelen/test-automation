import pytest

from data.test_data import CUSTOMER, ErrorMessages, Products

pytestmark = pytest.mark.ui


@pytest.mark.smoke
def test_complete_purchase_end_to_end(inventory_page):
    """Uçtan uca satın alma: sepete ekle -> sepeti kontrol et -> bilgileri gir -> tutarı doğrula -> bitir."""
    products = [Products.BACKPACK, Products.BOLT_TSHIRT]
    for product in products:
        inventory_page.add_to_cart(product)

    cart = inventory_page.go_to_cart()
    assert sorted(cart.item_names()) == sorted(products)

    overview = cart.checkout().continue_to_overview(**CUSTOMER)

    # Ara toplam, ürün fiyatlarının toplamı olmalı; genel toplam = ara toplam + vergi
    assert overview.subtotal == pytest.approx(sum(overview.item_prices()))
    assert overview.total == pytest.approx(overview.subtotal + overview.tax)

    complete = overview.finish()
    assert complete.header == "Thank you for your order!"


@pytest.mark.parametrize(
    ("first_name", "last_name", "postal_code", "expected_error"),
    [
        pytest.param("", "Test", "34000", ErrorMessages.FIRST_NAME_REQUIRED, id="ad-bos"),
        pytest.param("Yigit", "", "34000", ErrorMessages.LAST_NAME_REQUIRED, id="soyad-bos"),
        pytest.param("Yigit", "Test", "", ErrorMessages.POSTAL_CODE_REQUIRED, id="posta-kodu-bos"),
    ],
)
def test_checkout_form_requires_all_fields(inventory_page, first_name, last_name, postal_code, expected_error):
    inventory_page.add_to_cart(Products.BACKPACK)
    info_page = inventory_page.go_to_cart().checkout()

    info_page.fill_form(first_name, last_name, postal_code)

    assert info_page.error_message == expected_error
