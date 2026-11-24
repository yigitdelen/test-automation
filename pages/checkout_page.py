"""Ödeme akışının üç adımı: bilgi formu -> özet -> tamamlandı."""

import re

import allure
from selenium.webdriver.common.by import By

from pages.components.header import LoggedInPage


def _amount(text: str) -> float:
    """'Item total: $39.98' -> 39.98"""
    return float(re.search(r"\$([\d.]+)", text).group(1))


class CheckoutInfoPage(LoggedInPage):
    PATH = "checkout-step-one.html"

    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    CANCEL_BUTTON = (By.ID, "cancel")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")

    @allure.step("Ödeme bilgilerini doldur: {first_name} {last_name}, {postal_code}")
    def fill_form(self, first_name: str, last_name: str, postal_code: str) -> None:
        # Boş bırakılması istenen alanlara hiç yazmıyoruz.
        if first_name:
            self.type(self.FIRST_NAME, first_name)
        if last_name:
            self.type(self.LAST_NAME, last_name)
        if postal_code:
            self.type(self.POSTAL_CODE, postal_code)
        self.click(self.CONTINUE_BUTTON)

    def continue_to_overview(
        self, first_name: str, last_name: str, postal_code: str
    ) -> "CheckoutOverviewPage":
        self.fill_form(first_name, last_name, postal_code)
        page = CheckoutOverviewPage(self.driver)
        page.wait_until_loaded()
        return page

    @allure.step("Ödemeyi iptal et (bilgi formu)")
    def cancel(self):
        from pages.cart_page import CartPage

        self.click(self.CANCEL_BUTTON)
        cart = CartPage(self.driver)
        cart.wait_until_loaded()
        return cart

    @property
    def error_message(self) -> str:
        return self.text_of(self.ERROR)


class CheckoutOverviewPage(LoggedInPage):
    PATH = "checkout-step-two.html"

    ITEM_PRICES = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    ITEM_NAMES = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    SUBTOTAL = (By.CSS_SELECTOR, "[data-test='subtotal-label']")
    TAX = (By.CSS_SELECTOR, "[data-test='tax-label']")
    TOTAL = (By.CSS_SELECTOR, "[data-test='total-label']")
    FINISH_BUTTON = (By.ID, "finish")
    CANCEL_BUTTON = (By.ID, "cancel")

    def wait_until_loaded(self) -> None:
        self.wait_for_url(self.PATH)
        self.find(self.SUBTOTAL)

    def item_names(self) -> list[str]:
        return [e.text for e in self.find_all(self.ITEM_NAMES)]

    def item_prices(self) -> list[float]:
        return [_amount(e.text) for e in self.find_all(self.ITEM_PRICES)]

    @property
    def subtotal(self) -> float:
        return _amount(self.text_of(self.SUBTOTAL))

    @property
    def tax(self) -> float:
        return _amount(self.text_of(self.TAX))

    @property
    def total(self) -> float:
        return _amount(self.text_of(self.TOTAL))

    @allure.step("Siparişi tamamla")
    def finish(self) -> "CheckoutCompletePage":
        self.click(self.FINISH_BUTTON)
        page = CheckoutCompletePage(self.driver)
        page.wait_until_loaded()
        return page

    @allure.step("Ödemeyi iptal et (özet sayfası)")
    def cancel(self):
        from pages.inventory_page import InventoryPage

        self.click(self.CANCEL_BUTTON)
        inventory = InventoryPage(self.driver)
        inventory.wait_until_loaded()
        return inventory


class CheckoutCompletePage(LoggedInPage):
    PATH = "checkout-complete.html"

    COMPLETE_HEADER = (By.CSS_SELECTOR, "[data-test='complete-header']")
    BACK_HOME_BUTTON = (By.ID, "back-to-products")

    def wait_until_loaded(self) -> None:
        self.wait_for_url(self.PATH)
        self.find(self.COMPLETE_HEADER)

    @property
    def message(self) -> str:
        return self.text_of(self.COMPLETE_HEADER)

    @allure.step("Ana sayfaya dön")
    def back_home(self):
        from pages.inventory_page import InventoryPage

        self.click(self.BACK_HOME_BUTTON)
        inventory = InventoryPage(self.driver)
        inventory.wait_until_loaded()
        return inventory
