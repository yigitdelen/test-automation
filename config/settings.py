"""Projenin tüm ayarları tek yerde.

Her değer bir ortam değişkeniyle (environment variable) değiştirilebilir.
Örnek: HEADLESS=false pytest  -> tarayıcıyı görünür modda açar.
"""

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    # Test edilen siteler
    base_url: str = os.getenv("BASE_URL", "https://www.saucedemo.com")
    api_base_url: str = os.getenv("API_BASE_URL", "https://restful-booker.herokuapp.com")

    # Tarayıcı ayarları
    headless: bool = _env_bool("HEADLESS", True)
    window_size: str = os.getenv("WINDOW_SIZE", "1920,1080")
    explicit_wait: int = int(os.getenv("EXPLICIT_WAIT", "10"))

    # Boş bırakılırsa Selenium Manager tarayıcıyı ve sürücüyü kendisi bulur.
    chrome_binary: str | None = os.getenv("CHROME_BINARY") or None
    chromedriver_path: str | None = os.getenv("CHROMEDRIVER_PATH") or None

    # API ayarları (restful-booker'ın herkese açık demo kullanıcı bilgileri)
    api_username: str = os.getenv("API_USERNAME", "admin")
    api_password: str = os.getenv("API_PASSWORD", "password123")
    api_timeout: int = int(os.getenv("API_TIMEOUT", "15"))


settings = Settings()
