import pytest

from data.test_data import Products
from pages import InventoryPage

pytestmark = pytest.mark.ui


def test_inventory_shows_six_products(inventory_page):
    assert len(inventory_page.product_names()) == 6


@pytest.mark.parametrize(
    ("sort_value", "key", "reverse"),
    [
        pytest.param(InventoryPage.SORT_NAME_ASC, "name", False, id="isim-a-z"),
        pytest.param(InventoryPage.SORT_NAME_DESC, "name", True, id="isim-z-a"),
        pytest.param(InventoryPage.SORT_PRICE_ASC, "price", False, id="fiyat-artan"),
        pytest.param(InventoryPage.SORT_PRICE_DESC, "price", True, id="fiyat-azalan"),
    ],
)
def test_sorting_products(inventory_page, sort_value, key, reverse):
    inventory_page.sort_by(sort_value)

    values = inventory_page.product_names() if key == "name" else inventory_page.product_prices()
    assert values == sorted(values, reverse=reverse)


@pytest.mark.smoke
def test_add_products_updates_cart_badge(inventory_page):
    assert inventory_page.cart_count() == 0

    inventory_page.add_to_cart(Products.BACKPACK)
    assert inventory_page.cart_count() == 1

    inventory_page.add_to_cart(Products.BIKE_LIGHT)
    assert inventory_page.cart_count() == 2


def test_remove_product_updates_cart_badge(inventory_page):
    inventory_page.add_to_cart(Products.BACKPACK)
    inventory_page.add_to_cart(Products.BIKE_LIGHT)

    inventory_page.remove_from_cart(Products.BACKPACK)

    assert inventory_page.cart_count() == 1
    assert inventory_page.go_to_cart().item_names() == [Products.BIKE_LIGHT]
