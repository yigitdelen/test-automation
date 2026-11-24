import allure
from selenium.webdriver.common.by import By

from pages.components.header import LoggedInPage


class ProductPage(LoggedInPage):
    """Tek bir ürünün detay sayfası (inventory-item.html?id=...)."""

    PATH = "inventory-item.html"

    NAME = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    DESCRIPTION = (By.CSS_SELECTOR, "[data-test='inventory-item-desc']")
    PRICE = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, "[data-test='add-to-cart']")
    REMOVE_BUTTON = (By.CSS_SELECTOR, "[data-test='remove']")
    BACK_BUTTON = (By.CSS_SELECTOR, "[data-test='back-to-products']")

    def wait_until_loaded(self) -> None:
        self.wait_for_url(self.PATH)
        self.find(self.NAME)

    def info(self) -> dict:
        return {
            "name": self.text_of(self.NAME),
            "description": self.text_of(self.DESCRIPTION),
            "price": self.text_of(self.PRICE),
        }

    @allure.step("Detay sayfasından sepete ekle")
    def add_to_cart(self) -> None:
        self.click(self.ADD_TO_CART_BUTTON)

    @allure.step("Detay sayfasından sepetten çıkar")
    def remove_from_cart(self) -> None:
        self.click(self.REMOVE_BUTTON)

    def is_in_cart(self) -> bool:
        return self.is_visible(self.REMOVE_BUTTON, timeout=1)

    @allure.step("Ürünler sayfasına geri dön")
    def back_to_products(self):
        from pages.inventory_page import InventoryPage

        self.click(self.BACK_BUTTON)
        inventory = InventoryPage(self.driver)
        inventory.wait_until_loaded()
        return inventory
