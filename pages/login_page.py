from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    PATH = ""

    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")

    def login(self, username: str, password: str) -> None:
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def login_as(self, username: str, password: str) -> InventoryPage:
        """Başarılı giriş bekleyen testler için: girişten sonra ürünler sayfasını döndürür."""
        self.login(username, password)
        inventory = InventoryPage(self.driver)
        inventory.wait_until_loaded()
        return inventory

    @property
    def error_message(self) -> str:
        return self.text_of(self.ERROR)

    def is_displayed(self) -> bool:
        return self.is_visible(self.LOGIN_BUTTON)
