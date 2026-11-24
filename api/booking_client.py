"""restful-booker API'si için istemci.

Testler doğrudan URL yazmak yerine bu sınıfın metotlarını çağırır.
API adresi değişirse tek bir yeri düzeltmek yeterli olur.
Her istek ve cevap otomatik olarak loglanır ve Allure raporuna eklenir;
bir test kaldığında API'ye ne gönderildiğini ve ne döndüğünü rapordan görebilirsin.
Dokümantasyon: https://restful-booker.herokuapp.com/apidoc/index.html
"""

import json
import logging

import allure
import requests

from config.settings import settings

log = logging.getLogger(__name__)


def _pretty(body) -> str:
    if not body:
        return "(boş)"
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="replace")
    try:
        return json.dumps(json.loads(body), indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(body)


def _log_exchange(response: requests.Response, *args, **kwargs) -> None:
    request = response.request
    summary = (
        f"{request.method} {request.url}\n"
        f"Durum: {response.status_code} ({response.elapsed.total_seconds() * 1000:.0f} ms)\n\n"
        f"--- İstek gövdesi ---\n{_pretty(request.body)}\n\n"
        f"--- Cevap gövdesi ---\n{_pretty(response.content)}"
    )
    log.info("%s %s -> %s", request.method, request.url, response.status_code)
    allure.attach(
        summary,
        name=f"{request.method} {request.path_url} -> {response.status_code}",
        attachment_type=allure.attachment_type.TEXT,
    )


class BookingClient:
    def __init__(self, base_url: str = settings.api_base_url, timeout: int = settings.api_timeout):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        self.session.hooks["response"].append(_log_exchange)

    def _request(
        self,
        method: str,
        path: str,
        token: str | None = None,
        basic_auth: tuple[str, str] | None = None,
        **kwargs,
    ) -> requests.Response:
        headers = kwargs.pop("headers", {})
        if token:
            # restful-booker güncelleme ve silmede token'ı Cookie başlığında bekler.
            headers["Cookie"] = f"token={token}"
        return self.session.request(
            method,
            f"{self.base_url}{path}",
            headers=headers,
            auth=basic_auth,
            timeout=self.timeout,
            **kwargs,
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

    def get_booking(self, booking_id: int | str) -> requests.Response:
        return self._request("GET", f"/booking/{booking_id}")

    def create_booking(self, booking: dict) -> requests.Response:
        return self._request("POST", "/booking", json=booking)

    def create_booking_raw(self, body: str) -> requests.Response:
        """Gövdeyi olduğu gibi gönderir (bozuk JSON gibi negatif testler için)."""
        return self._request("POST", "/booking", data=body.encode("utf-8"))

    def update_booking(self, booking_id: int, booking: dict, **auth) -> requests.Response:
        return self._request("PUT", f"/booking/{booking_id}", json=booking, **auth)

    def partial_update_booking(self, booking_id: int, fields: dict, **auth) -> requests.Response:
        return self._request("PATCH", f"/booking/{booking_id}", json=fields, **auth)

    def delete_booking(self, booking_id: int, **auth) -> requests.Response:
        return self._request("DELETE", f"/booking/{booking_id}", **auth)
