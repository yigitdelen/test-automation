"""Ödeme akışının üç adımı: bilgi formu -> özet -> tamamlandı."""

import re

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


def _amount(text: str) -> float:
    """'Item total: $39.98' -> 39.98"""
    return float(re.search(r"\$([\d.]+)", text).group(1))


class CheckoutInfoPage(BasePage):
    PATH = "checkout-step-one.html"

    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")

    def fill_form(self, first_name: str, last_name: str, postal_code: str) -> None:
        # Boş bırakılması istenen alanlara hiç yazmıyoruz.
        if first_name:
            self.type(self.FIRST_NAME, first_name)
        if last_name:
            self.type(self.LAST_NAME, last_name)
        if postal_code:
            self.type(self.POSTAL_CODE, postal_code)
        self.click(self.CONTINUE_BUTTON)

    def continue_to_overview(self, first_name: str, last_name: str, postal_code: str) -> "CheckoutOverviewPage":
        self.fill_form(first_name, last_name, postal_code)
        return CheckoutOverviewPage(self.driver)

    @property
    def error_message(self) -> str:
        return self.text_of(self.ERROR)


class CheckoutOverviewPage(BasePage):
    PATH = "checkout-step-two.html"

    ITEM_PRICES = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    SUBTOTAL = (By.CSS_SELECTOR, "[data-test='subtotal-label']")
    TAX = (By.CSS_SELECTOR, "[data-test='tax-label']")
    TOTAL = (By.CSS_SELECTOR, "[data-test='total-label']")
    FINISH_BUTTON = (By.ID, "finish")

    def item_prices(self) -> list[float]:
        self.find(self.SUBTOTAL)
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

    def finish(self) -> "CheckoutCompletePage":
        self.click(self.FINISH_BUTTON)
        return CheckoutCompletePage(self.driver)


class CheckoutCompletePage(BasePage):
    PATH = "checkout-complete.html"

    HEADER = (By.CSS_SELECTOR, "[data-test='complete-header']")

    @property
    def header(self) -> str:
        return self.text_of(self.HEADER)
