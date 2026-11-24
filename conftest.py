"""pytest'in otomatik yüklediği ortak ayarlar (fixture'lar ve hook'lar).

- `driver` fixture'ı: her UI testi için temiz bir Chrome açar, test bitince kapatır.
- Kalan UI testlerinin ekran görüntüsü alınır ve HTML rapora eklenir.
"""

import re
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from config.settings import settings

SCREENSHOT_DIR = Path("reports/screenshots")


def _chrome_options() -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    if settings.headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={settings.window_size}")
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
    if settings.chrome_binary:
        options.binary_location = settings.chrome_binary
    return options


@pytest.fixture
def driver():
    service = Service(executable_path=settings.chromedriver_path) if settings.chromedriver_path else Service()
    browser = webdriver.Chrome(service=service, options=_chrome_options())
    yield browser
    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return
    browser = item.funcargs.get("driver")
    if browser is None:
        return

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    file_name = re.sub(r"[^\w.-]", "_", item.nodeid) + ".png"
    browser.save_screenshot(str(SCREENSHOT_DIR / file_name))

    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.png(browser.get_screenshot_as_base64(), name="Ekran görüntüsü"))
        report.extras = extras


def pytest_html_report_title(report):
    report.title = "Test Otomasyon Raporu"
