import allure
import pytest

from data.test_data import Products
from pages import InventoryPage

pytestmark = [pytest.mark.ui, allure.parent_suite("Web UI"), allure.suite("Ürün listesi")]


def test_inventory_lists_all_products(inventory_page):
    names = inventory_page.product_names()

    assert sorted(names) == sorted(Products.ALL)
    assert len(set(names)) == len(names), "Aynı ürün listede birden fazla kez görünüyor"


def test_all_prices_are_positive(inventory_page):
    prices = inventory_page.product_prices()

    assert len(prices) == len(Products.ALL)
    assert all(price > 0 for price in prices), f"Sıfır veya negatif fiyat var: {prices}"


def test_product_images_are_loaded_and_unique(inventory_page):
    assert inventory_page.broken_image_count() == 0
    assert len(set(inventory_page.image_sources())) == len(Products.ALL)


def test_default_sort_is_name_ascending(inventory_page):
    names = inventory_page.product_names()

    assert names == sorted(names)


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
    assert inventory_page.header.cart_count() == 0

    inventory_page.add_to_cart(Products.BACKPACK)
    assert inventory_page.header.cart_count() == 1
    assert inventory_page.is_marked_in_cart(Products.BACKPACK)

    inventory_page.add_to_cart(Products.BIKE_LIGHT)
    assert inventory_page.header.cart_count() == 2


def test_add_all_products_to_cart(inventory_page):
    for product in Products.ALL:
        inventory_page.add_to_cart(product)

    assert inventory_page.header.cart_count() == len(Products.ALL)


def test_remove_product_updates_cart_badge(inventory_page):
    inventory_page.add_to_cart(Products.BACKPACK)
    inventory_page.add_to_cart(Products.BIKE_LIGHT)

    inventory_page.remove_from_cart(Products.BACKPACK)

    assert inventory_page.header.cart_count() == 1
    assert not inventory_page.is_marked_in_cart(Products.BACKPACK)
    assert inventory_page.header.go_to_cart().item_names() == [Products.BIKE_LIGHT]


def test_cart_survives_page_refresh(driver, inventory_page):
    inventory_page.add_to_cart(Products.ONESIE)

    driver.refresh()
    inventory_page.wait_until_loaded()

    assert inventory_page.header.cart_count() == 1
    assert inventory_page.is_marked_in_cart(Products.ONESIE)


def test_reset_app_state_empties_cart(inventory_page):
    inventory_page.add_to_cart(Products.BACKPACK)
    inventory_page.add_to_cart(Products.BIKE_LIGHT)

    inventory_page.header.reset_app_state()

    assert inventory_page.header.cart_count() == 0
    assert inventory_page.header.go_to_cart().items() == []
