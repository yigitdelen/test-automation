from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.checkout_page import CheckoutInfoPage


class CartPage(BasePage):
    PATH = "cart.html"

    ITEM_NAMES = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    CHECKOUT_BUTTON = (By.ID, "checkout")

    def item_names(self) -> list[str]:
        self.find((By.CSS_SELECTOR, "[data-test='title']"))
        return [e.text for e in self.find_all(self.ITEM_NAMES)]

    def checkout(self) -> CheckoutInfoPage:
        self.click(self.CHECKOUT_BUTTON)
        return CheckoutInfoPage(self.driver)
