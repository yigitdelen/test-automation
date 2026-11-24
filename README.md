# Test Otomasyon Projesi

![Testler](https://github.com/yigitdelen/test-otomasyon/actions/workflows/tests.yml/badge.svg)

Python ile yazılmış web arayüzü (UI) ve API test otomasyonu projesi.

| Katman | Hedef | Araçlar |
|---|---|---|
| Web UI | [saucedemo.com](https://www.saucedemo.com) (demo e-ticaret sitesi) | Selenium, Page Object Model |
| API | [restful-booker](https://restful-booker.herokuapp.com/apidoc/index.html) (demo otel rezervasyon API'si) | requests, JSON Schema |
| Test çatısı | — | pytest, pytest-html |
| CI | Her push'ta otomatik çalışma | GitHub Actions |

## Neler test ediliyor?

**Web arayüzü (19 test)**
- Başarılı giriş, hatalı girişler (yanlış şifre, kilitli kullanıcı, boş alanlar), çıkış
- Giriş yapmadan korumalı sayfaya erişimin engellenmesi
- Ürün listesi ve sıralama (isim A-Z / Z-A, fiyat artan / azalan)
- Sepete ürün ekleme ve çıkarma
- Uçtan uca satın alma: sepet → bilgi formu → tutar kontrolü (ara toplam + vergi) → sipariş onayı
- Ödeme formunda zorunlu alan kontrolleri

**API (16 test)**
- Sağlık kontrolü, token alma (geçerli ve geçersiz bilgilerle)
- Rezervasyon CRUD: oluşturma (POST), okuma (GET), güncelleme (PUT / PATCH), silme (DELETE)
- Cevap yapısının JSON Schema ile doğrulanması
- Yetki kontrolleri: token olmadan veya geçersiz token ile güncelleme ve silmenin engellenmesi
- Filtreleme ve olmayan kayıt için 404

## Proje yapısı

```
├── api/
│   ├── booking_client.py   # API istemcisi: testler URL yerine bu metotları çağırır
│   └── schemas.py          # Cevapların beklenen yapısı (JSON Schema)
├── config/
│   └── settings.py         # URL'ler, tarayıcı ayarları (ortam değişkenleriyle değiştirilebilir)
├── data/
│   └── test_data.py        # Kullanıcılar, ürünler, hata mesajları, rezervasyon verisi üretici
├── pages/                  # Page Object Model: her sayfa bir sınıf
│   ├── base_page.py        # Ortak işlemler (bekle, tıkla, yaz)
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── tests/
│   ├── api/                # API testleri
│   └── ui/                 # Web arayüzü testleri
├── conftest.py             # Tarayıcıyı açıp kapatan fixture + kalan testte ekran görüntüsü
├── pytest.ini
└── requirements.txt
```

### Neden Page Object Model?

Sayfadaki elementlerin yerleri (locator) ve işlemleri sayfa sınıflarında durur, testler sadece
*ne yapıldığını* anlatır:

```python
inventory = login_page.login_as("standard_user", "secret_sauce")
inventory.add_to_cart("Sauce Labs Backpack")
assert inventory.cart_count() == 1
```

Sitede bir butonun id'si değişirse onlarca testi değil, tek bir sayfa sınıfını düzeltmek yeterli olur.

## Kurulum ve çalıştırma

Gereksinimler: Python 3.11+ ve Google Chrome.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

```bash
pytest                 # tüm testler
pytest -m api          # sadece API testleri
pytest -m ui           # sadece web testleri
pytest -m smoke        # sadece kritik akışlar
HEADLESS=false pytest -m ui   # tarayıcıyı görerek çalıştır
```

Rapor her çalıştırmadan sonra `reports/report.html` dosyasına yazılır. Kalan web testlerinin ekran
görüntüsü hem rapora eklenir hem de `reports/screenshots/` klasörüne kaydedilir.

### Ayarlar (ortam değişkenleri)

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `BASE_URL` | `https://www.saucedemo.com` | Web testlerinin hedefi |
| `API_BASE_URL` | `https://restful-booker.herokuapp.com` | API testlerinin hedefi |
| `HEADLESS` | `true` | `false` yapılırsa tarayıcı görünür açılır |
| `EXPLICIT_WAIT` | `10` | Element bekleme süresi (saniye) |
| `CHROME_BINARY` / `CHROMEDRIVER_PATH` | boş | Boşsa Selenium Manager Chrome'u ve sürücüyü kendisi bulur |

## CI (GitHub Actions)

`main` dalına her push'ta ve her pull request'te API ve UI testleri paralel iki iş olarak çalışır.
Sonuçlar deponun **Actions** sekmesinde görünür; HTML raporlar her çalıştırmanın altına
indirilebilir dosya (artifact) olarak eklenir. **Run workflow** butonuyla elle de başlatılabilir.

## Test edilen sistemin tuhaflıkları

Testler sırasında restful-booker API'sinin standartlara uymayan davranışları belgelendi:
- Hatalı girişte `401` yerine `200` döndürüp hatayı gövdede (`{"reason": "Bad credentials"}`) bildiriyor.
- Başarılı silmede `200`/`204` yerine `201 Created` döndürüyor.

Testler bu davranışları olduğu gibi doğruluyor ve kodda not olarak açıklıyor.
