"""restful-booker API'si için istemci.

Testler doğrudan URL yazmak yerine bu sınıfın metotlarını çağırır.
API adresi değişirse tek bir yeri düzeltmek yeterli olur.
Dokümantasyon: https://restful-booker.herokuapp.com/apidoc/index.html
"""

import requests

from config.settings import settings


class BookingClient:
    def __init__(self, base_url: str = settings.api_base_url, timeout: int = settings.api_timeout):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    def _request(self, method: str, path: str, token: str | None = None, **kwargs) -> requests.Response:
        headers = kwargs.pop("headers", {})
        if token:
            # restful-booker güncelleme ve silmede token'ı Cookie başlığında bekler.
            headers["Cookie"] = f"token={token}"
        return self.session.request(
            method, f"{self.base_url}{path}", headers=headers, timeout=self.timeout, **kwargs
        )

    # --- Sağlık kontrolü ---
    def ping(self) -> requests.Response:
        return self._request("GET", "/ping")

    # --- Kimlik doğrulama ---
    def create_token(self, username: str, password: str) -> requests.Response:
        return self._request("POST", "/auth", json={"username": username, "password": password})

    # --- Rezervasyonlar ---
    def get_booking_ids(self, **filters) -> requests.Response:
        return self._request("GET", "/booking", params=filters)

    def get_booking(self, booking_id: int) -> requests.Response:
        return self._request("GET", f"/booking/{booking_id}")

    def create_booking(self, booking: dict) -> requests.Response:
        return self._request("POST", "/booking", json=booking)

    def update_booking(self, booking_id: int, booking: dict, token: str | None = None) -> requests.Response:
        return self._request("PUT", f"/booking/{booking_id}", token=token, json=booking)

    def partial_update_booking(self, booking_id: int, fields: dict, token: str | None = None) -> requests.Response:
        return self._request("PATCH", f"/booking/{booking_id}", token=token, json=fields)

    def delete_booking(self, booking_id: int, token: str | None = None) -> requests.Response:
        return self._request("DELETE", f"/booking/{booking_id}", token=token)
