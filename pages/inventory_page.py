from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage


def product_slug(name: str) -> str:
    """'Sauce Labs Backpack' -> 'sauce-labs-backpack' (sitedeki buton id'leri bu formatta)."""
    return name.lower().replace(" ", "-")


class InventoryPage(BasePage):
    PATH = "inventory.html"

    TITLE = (By.CSS_SELECTOR, "[data-test='title']")
    ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    ITEM_NAMES = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    ITEM_PRICES = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    SORT_DROPDOWN = (By.CSS_SELECTOR, "[data-test='product-sort-container']")
    CART_BADGE = (By.CSS_SELECTOR, "[data-test='shopping-cart-badge']")
    CART_LINK = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    # Sıralama seçeneklerinin sitedeki değerleri
    SORT_NAME_ASC = "az"
    SORT_NAME_DESC = "za"
    SORT_PRICE_ASC = "lohi"
    SORT_PRICE_DESC = "hilo"

    def wait_until_loaded(self) -> None:
        self.find(self.TITLE)

    @property
    def title(self) -> str:
        return self.text_of(self.TITLE)

    def product_names(self) -> list[str]:
        return [e.text for e in self.find_all(self.ITEM_NAMES)]

    def product_prices(self) -> list[float]:
        return [float(e.text.replace("$", "")) for e in self.find_all(self.ITEM_PRICES)]

    def sort_by(self, value: str) -> None:
        Select(self.find(self.SORT_DROPDOWN)).select_by_value(value)

    def add_to_cart(self, product_name: str) -> None:
        self.click((By.CSS_SELECTOR, f"[data-test='add-to-cart-{product_slug(product_name)}']"))

    def remove_from_cart(self, product_name: str) -> None:
        self.click((By.CSS_SELECTOR, f"[data-test='remove-{product_slug(product_name)}']"))

    def cart_count(self) -> int:
        """Sepet ikonundaki sayı; sepet boşsa ikon hiç görünmez, o zaman 0 döner."""
        badges = self.find_all(self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    def go_to_cart(self):
        from pages.cart_page import CartPage

        self.click(self.CART_LINK)
        return CartPage(self.driver)

    def logout(self) -> None:
        self.click(self.MENU_BUTTON)
        self.click(self.LOGOUT_LINK)
