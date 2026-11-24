import allure
from selenium.webdriver.common.by import By

from pages.checkout_page import CheckoutInfoPage
from pages.components.header import LoggedInPage


class CartPage(LoggedInPage):
    PATH = "cart.html"

    ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    CONTINUE_SHOPPING_BUTTON = (By.ID, "continue-shopping")

    def wait_until_loaded(self) -> None:
        self.wait_for_url(self.PATH)
        self.find(self.TITLE)

    def items(self) -> list[dict]:
        """Sepetteki ürünler: [{'name': ..., 'price': 29.99, 'quantity': 1}, ...]"""
        result = []
        for item in self.find_all(self.ITEMS):
            result.append(
                {
                    "name": item.find_element(By.CSS_SELECTOR, "[data-test='inventory-item-name']").text,
                    "price": float(
                        item.find_element(By.CSS_SELECTOR, "[data-test='inventory-item-price']").text[1:]
                    ),
                    "quantity": int(item.find_element(By.CSS_SELECTOR, "[data-test='item-quantity']").text),
                }
            )
        return result

    def item_names(self) -> list[str]:
        return [item["name"] for item in self.items()]

    @allure.step("Sepet sayfasında ürünü çıkar: {product_name}")
    def remove(self, product_name: str) -> None:
        item = self.find(
            (
                By.XPATH,
                "//div[@data-test='inventory-item']"
                f"[.//div[@data-test='inventory-item-name' and text()='{product_name}']]",
            )
        )
        item.find_element(By.CSS_SELECTOR, "button[data-test^='remove']").click()

    @allure.step("Alışverişe devam et")
    def continue_shopping(self):
        from pages.inventory_page import InventoryPage

        self.click(self.CONTINUE_SHOPPING_BUTTON)
        inventory = InventoryPage(self.driver)
        inventory.wait_until_loaded()
        return inventory

    @allure.step("Ödemeye geç")
    def checkout(self) -> CheckoutInfoPage:
        self.click(self.CHECKOUT_BUTTON)
        page = CheckoutInfoPage(self.driver)
        page.wait_until_loaded()
        return page
