"""Tarayıcı fabrikası: istenen tarayıcıyı doğru ayarlarla açar.

Yeni bir tarayıcı (ör. Edge) eklemek için sadece bu dosyaya bir fonksiyon eklemek yeterli;
testlerde hiçbir değişiklik gerekmez.
"""

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from config.settings import settings

SUPPORTED_BROWSERS = ("chrome", "firefox")


def _chrome(headless: bool) -> WebDriver:
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={settings.window_width},{settings.window_height}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Chrome'un "şifreniz sızdırıldı" / "şifreyi kaydet" pencereleri testleri bölmesin.
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        },
    )
    if settings.browser_binary:
        options.binary_location = settings.browser_binary
    service = webdriver.ChromeService(executable_path=settings.driver_path)
    return webdriver.Chrome(service=service, options=options)


def _firefox(headless: bool) -> WebDriver:
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("-headless")
    options.add_argument(f"--width={settings.window_width}")
    options.add_argument(f"--height={settings.window_height}")
    if settings.browser_binary:
        options.binary_location = settings.browser_binary
    service = webdriver.FirefoxService(executable_path=settings.driver_path)
    return webdriver.Firefox(service=service, options=options)


def create_driver(browser: str, headless: bool) -> WebDriver:
    factories = {"chrome": _chrome, "firefox": _firefox}
    if browser not in factories:
        raise ValueError(f"Desteklenmeyen tarayıcı: {browser!r}. Seçenekler: {', '.join(SUPPORTED_BROWSERS)}")
    driver = factories[browser](headless)
    # Firefox pencere boyutunu argümanla her zaman uygulamayabiliyor; garantiye alalım.
    driver.set_window_size(settings.window_width, settings.window_height)
    return driver
