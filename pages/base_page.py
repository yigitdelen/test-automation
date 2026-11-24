"""Tüm sayfa sınıflarının ortak atası.

Elemente tıklama, yazı yazma, bekleme gibi işlemler burada bir kez yazılır;
sayfa sınıfları sadece kendi elementlerini (locator) ve işlemlerini tanımlar.

Not: `time.sleep()` hiç kullanılmıyor. Her işlem, elementin hazır olmasını
akıllıca bekleyen WebDriverWait ile yapılıyor (explicit wait). Bu, testleri
hem hızlı hem de kararlı (flaky olmayan) yapar.
"""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings

Locator = tuple[str, str]


class BasePage:
    PATH = ""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, settings.explicit_wait)

    def open(self):
        self.driver.get(f"{settings.base_url}/{self.PATH}")
        return self

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    def find(self, locator: Locator) -> WebElement:
        """Element görünür olana kadar bekler ve döndürür."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: Locator) -> list[WebElement]:
        """Eşleşen tüm elementleri döndürür (hiç yoksa boş liste)."""
        return self.driver.find_elements(*locator)

    def click(self, locator: Locator) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator: Locator, text: str) -> None:
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def text_of(self, locator: Locator) -> str:
        return self.find(locator).text

    def value_of(self, locator: Locator) -> str:
        """Form alanının içindeki değeri döndürür."""
        return self.find(locator).get_attribute("value")

    def is_visible(self, locator: Locator, timeout: float = 2) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def wait_for_url(self, path: str) -> None:
        self.wait.until(EC.url_contains(path))
