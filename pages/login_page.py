import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    PATH = ""

    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")
    ERROR_CLOSE_BUTTON = (By.CSS_SELECTOR, "[data-test='error-button']")

    # saucedemo girişten sonra kullanıcı adını bu çereze (cookie) yazıyor
    SESSION_COOKIE = "session-username"

    @allure.step("Giriş yap: kullanıcı={username}")
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

    @allure.step("Çerez ile hızlı giriş: kullanıcı={username}")
    def login_with_session_cookie(self, username: str) -> InventoryPage:
        """Giriş formunu kullanmadan, oturum çerezini doğrudan yazarak giriş yapar.

        Girişin kendisini test etmeyen testlerde (sepet, sıralama, ödeme...) her seferinde
        formu doldurmak zaman kaybıdır. Gerçek projelerde de bu yöntem (çerez ya da API ile
        giriş) sık kullanılır. Girişin doğru çalıştığı ise test_login.py'de ayrıca test edilir.
        """
        self.driver.add_cookie({"name": self.SESSION_COOKIE, "value": username})
        return InventoryPage(self.driver).open()

    @property
    def error_message(self) -> str:
        return self.text_of(self.ERROR)

    def has_error(self) -> bool:
        return self.is_visible(self.ERROR, timeout=1)

    @allure.step("Hata mesajını kapat")
    def close_error(self) -> None:
        self.click(self.ERROR_CLOSE_BUTTON)

    def password_field_type(self) -> str:
        return self.find(self.PASSWORD).get_attribute("type")

    def is_displayed(self) -> bool:
        return self.is_visible(self.LOGIN_BUTTON)
