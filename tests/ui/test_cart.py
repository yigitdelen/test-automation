import allure
import pytest

from data.test_data import PASSWORD, Products, Users

pytestmark = [pytest.mark.ui, allure.parent_suite("Web UI"), allure.suite("Sepet")]


def test_cart_is_empty_initially(inventory_page):
    cart = inventory_page.header.go_to_cart()

    assert cart.items() == []


def test_cart_shows_added_products_with_correct_price_and_quantity(inventory_page):
    products = [Products.BACKPACK, Products.ONESIE]
    expected_prices = {}
    for product in products:
        expected_prices[product] = float(inventory_page.product_info(product)["price"][1:])
        inventory_page.add_to_cart(product)

    items = inventory_page.header.go_to_cart().items()

    assert {item["name"] for item in items} == set(products)
    for item in items:
        assert item["quantity"] == 1
        assert item["price"] == expected_prices[item["name"]]


def test_remove_product_on_cart_page(inventory_page):
    inventory_page.add_to_cart(Products.BACKPACK)
    inventory_page.add_to_cart(Products.BIKE_LIGHT)
    cart = inventory_page.header.go_to_cart()

    cart.remove(Products.BACKPACK)

    assert cart.item_names() == [Products.BIKE_LIGHT]
    assert cart.header.cart_count() == 1


def test_continue_shopping_keeps_cart(inventory_page):
    inventory_page.add_to_cart(Products.BOLT_TSHIRT)
    cart = inventory_page.header.go_to_cart()

    inventory = cart.continue_shopping()

    assert inventory.header.cart_count() == 1
    assert inventory.is_marked_in_cart(Products.BOLT_TSHIRT)


def test_cart_is_kept_after_logout_and_login(login_page):
    """Site sepeti tarayıcıda sakladığı için çıkış yapıp tekrar girince sepet korunuyor."""
    inventory = login_page.login_as(Users.STANDARD, PASSWORD)
    inventory.add_to_cart(Products.BACKPACK)
    inventory.header.logout()

    inventory = login_page.login_as(Users.STANDARD, PASSWORD)

    assert inventory.header.cart_count() == 1
    assert inventory.header.go_to_cart().item_names() == [Products.BACKPACK]
