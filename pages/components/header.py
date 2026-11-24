"""Giriş yapıldıktan sonra her sayfanın üstünde görünen bölüm: yan menü ve sepet ikonu.

Bu bölüm birçok sayfada tekrarlandığı için ayrı bir "bileşen" (component) olarak yazıldı.
Sayfalar onu `self.header` olarak kullanır: inventory.header.cart_count()
"""

import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class Header(BasePage):
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    ALL_ITEMS_LINK = (By.ID, "inventory_sidebar_link")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")
    RESET_LINK = (By.ID, "reset_sidebar_link")
    CLOSE_MENU_BUTTON = (By.ID, "react-burger-cross-btn")
    CART_BADGE = (By.CSS_SELECTOR, "[data-test='shopping-cart-badge']")
    CART_LINK = (By.CSS_SELECTOR, "[data-test='shopping-cart-link']")

    def _open_menu(self) -> None:
        self.click(self.MENU_BUTTON)

    @allure.step("Menüden çıkış yap")
    def logout(self) -> None:
        self._open_menu()
        self.click(self.LOGOUT_LINK)

    @allure.step("Menüden uygulama durumunu sıfırla")
    def reset_app_state(self) -> None:
        self._open_menu()
        self.click(self.RESET_LINK)
        self.click(self.CLOSE_MENU_BUTTON)

    def cart_count(self) -> int:
        """Sepet ikonundaki sayı; sepet boşsa ikon hiç görünmez, o zaman 0 döner."""
        badges = self.find_all(self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    @allure.step("Sepete git")
    def go_to_cart(self):
        from pages.cart_page import CartPage  # döngüsel import'u önlemek için burada

        self.click(self.CART_LINK)
        cart = CartPage(self.driver)
        cart.wait_until_loaded()
        return cart


class LoggedInPage(BasePage):
    """Giriş yapılmış kullanıcının gördüğü sayfaların ortak atası (üst bölümü içerir)."""

    TITLE = (By.CSS_SELECTOR, "[data-test='title']")

    def __init__(self, driver):
        super().__init__(driver)
        self.header = Header(driver)

    def wait_until_loaded(self) -> None:
        self.wait_for_url(self.PATH)

    @property
    def title(self) -> str:
        return self.text_of(self.TITLE)
