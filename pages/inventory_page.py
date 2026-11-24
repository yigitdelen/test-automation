import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select

from pages.components.header import LoggedInPage


class InventoryPage(LoggedInPage):
    PATH = "inventory.html"

    ITEMS = (By.CSS_SELECTOR, "[data-test='inventory-item']")
    ITEM_NAMES = (By.CSS_SELECTOR, "[data-test='inventory-item-name']")
    ITEM_PRICES = (By.CSS_SELECTOR, "[data-test='inventory-item-price']")
    ITEM_IMAGES = (By.CSS_SELECTOR, "img.inventory_item_img")
    SORT_DROPDOWN = (By.CSS_SELECTOR, "[data-test='product-sort-container']")

    # Sıralama seçeneklerinin sitedeki değerleri
    SORT_NAME_ASC = "az"
    SORT_NAME_DESC = "za"
    SORT_PRICE_ASC = "lohi"
    SORT_PRICE_DESC = "hilo"

    def open(self):
        super().open()
        self.wait_until_loaded()
        return self

    def wait_until_loaded(self) -> None:
        self.find(self.TITLE)

    # --- Ürün listesi ---

    def product_names(self) -> list[str]:
        return [e.text for e in self.find_all(self.ITEM_NAMES)]

    def product_prices(self) -> list[float]:
        return [float(e.text.replace("$", "")) for e in self.find_all(self.ITEM_PRICES)]

    def _card(self, product_name: str) -> WebElement:
        """Adı verilen ürünün kartını (resim, isim, açıklama, fiyat, buton) bulur."""
        return self.find(
            (
                By.XPATH,
                "//div[@data-test='inventory-item']"
                f"[.//div[@data-test='inventory-item-name' and text()='{product_name}']]",
            )
        )

    def product_info(self, product_name: str) -> dict:
        card = self._card(product_name)
        return {
            "name": card.find_element(By.CSS_SELECTOR, "[data-test='inventory-item-name']").text,
            "description": card.find_element(By.CSS_SELECTOR, "[data-test='inventory-item-desc']").text,
            "price": card.find_element(By.CSS_SELECTOR, "[data-test='inventory-item-price']").text,
        }

    def image_sources(self) -> list[str]:
        return [img.get_attribute("src") for img in self.find_all(self.ITEM_IMAGES)]

    def broken_image_count(self) -> int:
        """Yüklenemeyen (genişliği 0 olan) ürün görsellerinin sayısı."""
        return self.driver.execute_script(
            "return [...document.querySelectorAll('img.inventory_item_img')]"
            ".filter(img => !img.complete || img.naturalWidth === 0).length"
        )

    # --- İşlemler ---

    @allure.step("Ürünleri sırala: {value}")
    def sort_by(self, value: str) -> None:
        Select(self.find(self.SORT_DROPDOWN)).select_by_value(value)

    @allure.step("Sepete ekle: {product_name}")
    def add_to_cart(self, product_name: str) -> None:
        self._card(product_name).find_element(By.CSS_SELECTOR, "button[data-test^='add-to-cart']").click()

    @allure.step("Sepetten çıkar: {product_name}")
    def remove_from_cart(self, product_name: str) -> None:
        self._card(product_name).find_element(By.CSS_SELECTOR, "button[data-test^='remove']").click()

    def is_marked_in_cart(self, product_name: str) -> bool:
        """Ürün kartındaki buton 'Remove' ise ürün sepette görünüyor demektir."""
        button = self._card(product_name).find_element(By.TAG_NAME, "button")
        return button.get_attribute("data-test").startswith("remove")

    @allure.step("Ürün detayını aç: {product_name}")
    def open_product(self, product_name: str):
        from pages.product_page import ProductPage

        self._card(product_name).find_element(By.CSS_SELECTOR, "[data-test='inventory-item-name']").click()
        page = ProductPage(self.driver)
        page.wait_until_loaded()
        return page
