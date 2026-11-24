"""Test edilen sitede bulunan gerçek hatalar.

Bu testler sitenin *olması gereken* davranışını kontrol eder; site şu an hatalı olduğu için
kalırlar ve `xfail` (beklenen hata) olarak işaretlenmiştir. Raporda "XFAIL" olarak görünürler.

Ayar `xfail_strict = true` olduğu için, hata bir gün düzeltilirse bu testler geçer ve
"XPASS(strict)" olarak KIRMIZI yanar. Böylece hatanın düzeltildiğinden haberdar olur,
xfail işaretini kaldırırız.

Not: saucedemo'daki problem_user bilerek hatalı yapılmış bir kullanıcıdır; bu dosya,
otomasyonun gerçek hataları nasıl yakalayıp belgelediğini göstermek için var.
"""

import allure
import pytest

from data.test_data import Products, Users
from pages import InventoryPage

pytestmark = [
    pytest.mark.ui,
    pytest.mark.known_bug,
    allure.parent_suite("Web UI"),
    allure.suite("Bilinen hatalar"),
]


@pytest.mark.xfail(reason="HATA: problem_user'da tüm ürünler aynı (kırık) görseli gösteriyor")
def test_problem_user_sees_correct_product_images(login_as):
    inventory = login_as(Users.PROBLEM)

    assert len(set(inventory.image_sources())) == len(Products.ALL)


@pytest.mark.xfail(reason="HATA: problem_user'da sıralama menüsü çalışmıyor, liste değişmiyor")
def test_problem_user_can_sort_products(login_as):
    inventory = login_as(Users.PROBLEM)

    inventory.sort_by(InventoryPage.SORT_NAME_DESC)

    names = inventory.product_names()
    assert names == sorted(names, reverse=True)


@pytest.mark.parametrize(
    "product",
    [
        pytest.param(Products.BACKPACK, id="backpack-calisiyor"),
        pytest.param(
            Products.BOLT_TSHIRT,
            marks=pytest.mark.xfail(reason="HATA: problem_user bu ürünü sepete ekleyemiyor"),
            id="bolt-tshirt",
        ),
        pytest.param(
            Products.FLEECE_JACKET,
            marks=pytest.mark.xfail(reason="HATA: problem_user bu ürünü sepete ekleyemiyor"),
            id="fleece-jacket",
        ),
        pytest.param(
            Products.RED_TSHIRT,
            marks=pytest.mark.xfail(reason="HATA: problem_user bu ürünü sepete ekleyemiyor"),
            id="red-tshirt",
        ),
    ],
)
def test_problem_user_can_add_product_to_cart(login_as, product):
    inventory = login_as(Users.PROBLEM)

    inventory.add_to_cart(product)

    assert inventory.header.cart_count() == 1


@pytest.mark.xfail(reason="HATA: problem_user sepete eklediği ürünü listeden çıkaramıyor")
def test_problem_user_can_remove_product_from_cart(login_as):
    inventory = login_as(Users.PROBLEM)
    inventory.add_to_cart(Products.BACKPACK)

    inventory.remove_from_cart(Products.BACKPACK)

    assert inventory.header.cart_count() == 0


@pytest.mark.xfail(
    reason="HATA: 'Reset App State' sepeti boşaltıyor ama ürün butonları 'Remove' olarak kalıyor"
)
def test_reset_app_state_resets_product_buttons(inventory_page):
    """Bu hata standard_user'da da var: sepet sayacı sıfırlanıyor ama butonlar eski hâlinde kalıyor."""
    inventory_page.add_to_cart(Products.BACKPACK)

    inventory_page.header.reset_app_state()

    assert not inventory_page.is_marked_in_cart(Products.BACKPACK)
