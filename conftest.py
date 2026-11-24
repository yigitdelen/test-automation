"""pytest'in otomatik yüklediği ortak ayarlar (fixture'lar ve hook'lar).

- Komut satırı seçenekleri: --browser chrome|firefox, --headed
- `driver` fixture'ı: her UI testi için temiz bir tarayıcı açar, test bitince kapatır.
- Kalan UI testlerinin ekran görüntüsü alınır; hem HTML rapora hem Allure raporuna eklenir.
"""

import platform
import re
import shutil
from pathlib import Path

import allure
import pytest

from config.settings import settings
from utils.driver_factory import SUPPORTED_BROWSERS, create_driver

SCREENSHOT_DIR = Path("reports/screenshots")
CATEGORIES_FILE = Path(__file__).parent / "config" / "allure_categories.json"


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        default=settings.browser,
        choices=SUPPORTED_BROWSERS,
        help="UI testlerinin çalışacağı tarayıcı (varsayılan: chrome)",
    )
    parser.addoption(
        "--headed",
        action="store_true",
        default=not settings.headless,
        help="Tarayıcıyı görünür modda aç (varsayılan: görünmez / headless)",
    )


@pytest.fixture(scope="session")
def browser_name(pytestconfig) -> str:
    return pytestconfig.getoption("--browser")


@pytest.fixture
def driver(pytestconfig, browser_name):
    # Tarayıcı adı Allure'da parametre olarak görünür; böylece aynı test Chrome ve Firefox'ta
    # çalıştığında rapor ikisini ayrı sonuç olarak gösterir (birbirinin tekrarı sanmaz).
    allure.dynamic.parameter("Tarayıcı", browser_name)
    browser = create_driver(browser_name, headless=not pytestconfig.getoption("--headed"))
    yield browser
    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # Sadece test gövdesinde ya da hazırlıkta (fixture) kalan UI testleri için
    if report.when not in ("setup", "call") or not report.failed:
        return
    browser = item.funcargs.get("driver")
    if browser is None:
        return

    png = browser.get_screenshot_as_png()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    file_name = re.sub(r"[^\w.-]", "_", item.nodeid) + ".png"
    (SCREENSHOT_DIR / file_name).write_bytes(png)

    allure.attach(png, name="Ekran görüntüsü", attachment_type=allure.attachment_type.PNG)
    allure.attach(browser.current_url, name="Sayfa adresi", attachment_type=allure.attachment_type.TEXT)

    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.png(browser.get_screenshot_as_base64(), name="Ekran görüntüsü"))
        extras.append(pytest_html.extras.url(browser.current_url, name="Sayfa adresi"))
        report.extras = extras


def pytest_html_report_title(report):
    report.title = "Test Otomasyon Raporu"


def pytest_sessionfinish(session):
    """Allure raporuna ortam bilgisi ve hata kategorilerini ekler.

    Paralel çalışmada (xdist) her işçi de bu fonksiyonu çağırır; dosyaları sadece ana süreç yazar.
    """
    if hasattr(session.config, "workerinput"):
        return
    alluredir = session.config.getoption("--alluredir", default=None)
    if not alluredir:
        return

    results_dir = Path(alluredir)
    results_dir.mkdir(parents=True, exist_ok=True)

    environment = {
        "Tarayıcı": session.config.getoption("--browser"),
        "Görünmez mod (headless)": str(not session.config.getoption("--headed")),
        "Web sitesi": settings.base_url,
        "API": settings.api_base_url,
        "Python": platform.python_version(),
        "İşletim sistemi": platform.system(),
    }
    # .properties formatında anahtardaki boşluklar "\ " şeklinde yazılır
    lines = [key.replace(" ", "\\ ") + f"={value}" for key, value in environment.items()]
    (results_dir / "environment.properties").write_text("\n".join(lines), encoding="utf-8")

    shutil.copy(CATEGORIES_FILE, results_dir / "categories.json")
