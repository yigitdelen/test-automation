import allure
import pytest

from data.test_data import Products

pytestmark = [pytest.mark.ui, allure.parent_suite("Web UI"), allure.suite("Ürün detayı")]


@pytest.mark.parametrize("product", Products.ALL)
def test_detail_page_matches_product_card(inventory_page, product):
    """Listede görünen isim, açıklama ve fiyat, detay sayfasındakiyle birebir aynı olmalı."""
    card_info = inventory_page.product_info(product)

    detail = inventory_page.open_product(product)

    assert detail.info() == card_info


def test_add_to_cart_from_detail_page(inventory_page):
    detail = inventory_page.open_product(Products.FLEECE_JACKET)

    detail.add_to_cart()

    assert detail.is_in_cart()
    assert detail.header.cart_count() == 1
    inventory = detail.back_to_products()
    assert inventory.is_marked_in_cart(Products.FLEECE_JACKET)


def test_remove_from_cart_on_detail_page(inventory_page):
    inventory_page.add_to_cart(Products.FLEECE_JACKET)
    detail = inventory_page.open_product(Products.FLEECE_JACKET)
    assert detail.is_in_cart()

    detail.remove_from_cart()

    assert not detail.is_in_cart()
    assert detail.header.cart_count() == 0


def test_back_to_products_button(inventory_page):
    detail = inventory_page.open_product(Products.BACKPACK)

    inventory = detail.back_to_products()

    assert inventory.title == "Products"
