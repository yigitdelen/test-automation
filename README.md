# Test Otomasyon Projesi

[![Testler](https://github.com/yigitdelen/test-automation/actions/workflows/tests.yml/badge.svg)](https://github.com/yigitdelen/test-automation/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Selenium](https://img.shields.io/badge/selenium-4-43B02A)
![pytest](https://img.shields.io/badge/pytest-9-0A9EDC)

Python ile yazılmış web arayüzü (UI) ve API test otomasyonu projesi.
**117 test** · Chrome + Firefox · paralel çalışma · Allure raporu · her push'ta ve her gece otomatik çalışma.

📊 **[Canlı test raporu (Allure)](https://yigitdelen.github.io/test-automation/)**: her push'ta ve her gece
otomatik güncellenir. Testleri, bulunan hataları, ekran görüntülerini ve API isteklerini kurulum yapmadan
inceleyebilirsin.

| Katman | Hedef | Araçlar |
|---|---|---|
| Web UI | [saucedemo.com](https://www.saucedemo.com) (demo e-ticaret sitesi) | Selenium 4, Page Object Model |
| API | [restful-booker](https://restful-booker.herokuapp.com/apidoc/index.html) (demo otel rezervasyon API'si) | requests, JSON Schema |
| Test çatısı | — | pytest, pytest-xdist (paralel), pytest-rerunfailures |
| Test verisi | — | Faker (Türkçe rastgele veri) |
| Raporlama | — | Allure, pytest-html |
| Kod kalitesi | — | ruff |
| CI | GitHub Actions | lint → API + UI (Chrome, Firefox) → Allure raporu |

## Neler test ediliyor?

### Web arayüzü — 64 test

| Alan | Senaryolar |
|---|---|
| **Giriş** | Başarılı giriş, tüm kullanıcı tipleriyle giriş, 8 farklı hatalı giriş (yanlış şifre, kilitli kullanıcı, boş alanlar, büyük/küçük harf, SQL injection denemesi), hata mesajını kapatma, şifre alanının gizli olması, çıkış, girişsiz erişimin engellenmesi |
| **Ürün listesi** | Tüm ürünlerin listelenmesi, fiyatların geçerliliği, görsellerin yüklenmesi, 4 farklı sıralama, sepete ekleme/çıkarma, sayfa yenilenince sepetin korunması, uygulama durumunu sıfırlama |
| **Ürün detayı** | 6 ürünün her biri için liste ile detay sayfasındaki bilgilerin tutarlılığı, detaydan sepete ekleme/çıkarma, geri dönme |
| **Sepet** | Fiyat ve adet doğruluğu, sepetten ürün çıkarma, alışverişe devam etme, çıkış yapıp girince sepetin korunması |
| **Ödeme** | Uçtan uca satın alma, 3 farklı sepet için tutar hesabı (ara toplam + %8 vergi), zorunlu alan kontrolleri, iki farklı adımda iptal etme |

### API — 53 test

| Alan | Senaryolar |
|---|---|
| **Kimlik doğrulama** | Sağlık kontrolü, token alma, her girişte yeni token, 4 farklı hatalı giriş |
| **CRUD** | Oluşturma (7 farklı veri seti: Türkçe karakter, emoji, sınır değerler...), okuma, tam ve kısmi güncelleme, silme, uçtan uca yaşam döngüsü |
| **Yetki** | Token olmadan, geçersiz token ve yanlış şifreyle güncelleme/silme engelleniyor mu; engellenince veri gerçekten değişmemiş mi |
| **Filtreleme** | İsim, soyisim ve tarihe göre arama |
| **Girdi doğrulama** | Bozuk JSON, eksik zorunlu alanlar, geçersiz fiyat ve tarihler |
| **Diğer** | JSON Schema ile cevap yapısı, `Content-Type` başlığı, cevap süresi |

## 🐞 Bulunan hatalar

Testler, test edilen sistemlerde **17 gerçek hata** buldu. Bunlar `xfail` (beklenen hata) olarak
işaretlenip belgelendi: testler *olması gereken* davranışı kontrol ediyor, sistem hatalı olduğu için
kalıyor ve raporda ayrı bir kategoride görünüyor.

`xfail_strict = true` ayarı sayesinde bir hata düzeltilirse ilgili test **kırmızı yanar**
(XPASS) ve haberdar oluruz.

| Sistem | Hata | Test |
|---|---|---|
| saucedemo | `problem_user`'da tüm ürün görselleri aynı (kırık) görsel | `test_known_bugs.py` |
| saucedemo | `problem_user`'da sıralama çalışmıyor | `test_known_bugs.py` |
| saucedemo | `problem_user` 3 ürünü sepete ekleyemiyor | `test_known_bugs.py` |
| saucedemo | `problem_user` sepetteki ürünü çıkaramıyor | `test_known_bugs.py` |
| saucedemo | "Reset App State" sepeti boşaltıyor ama butonlar "Remove" olarak kalıyor (`standard_user`'da da var) | `test_known_bugs.py` |
| restful-booker | Zorunlu alan eksikse 400 yerine **500 sunucu hatası** (5 alan) | `test_booking_validation.py` |
| restful-booker | Boş gövdede 500 sunucu hatası | `test_booking_validation.py` |
| restful-booker | Metin fiyat, negatif fiyat, geçersiz tarih ve çıkışı girişten önce olan rezervasyon **kabul ediliyor** | `test_booking_validation.py` |

Ayrıca standartlara uymayan ama tutarlı davranışlar testlerde not olarak açıklandı:
hatalı girişte `401` yerine `200`, başarılı silmede `201`, olmayan kayıtta `404` yerine `405`.

## Proje yapısı

```
├── api/
│   ├── booking_client.py     # API istemcisi; her istek/cevabı loglar ve rapora ekler
│   └── schemas.py            # Cevapların beklenen yapısı (JSON Schema)
├── config/
│   ├── settings.py           # URL, tarayıcı, bekleme süresi... (ortam değişkenleriyle değişir)
│   └── allure_categories.json  # Raporda hataların sınıflandırılması
├── data/
│   └── test_data.py          # Sabit veriler + Faker ile rastgele veri üreticiler
├── pages/                    # Page Object Model
│   ├── base_page.py          # Ortak işlemler (bekle, tıkla, yaz)
│   ├── components/
│   │   └── header.py         # Her sayfadaki menü ve sepet ikonu (bileşen)
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── product_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── utils/
│   └── driver_factory.py     # Chrome / Firefox'u doğru ayarlarla açar
├── tests/
│   ├── api/                  # API testleri
│   └── ui/                   # Web arayüzü testleri
├── conftest.py               # Tarayıcı fixture'ı, komut satırı seçenekleri, ekran görüntüsü
└── pyproject.toml            # pytest ve ruff ayarları
```

## Kullanılan teknikler

**Page Object Model + bileşenler.** Sayfadaki elementler ve işlemler sayfa sınıflarında durur,
testler sadece *ne yapıldığını* anlatır. Her sayfada tekrarlanan menü ve sepet ikonu ayrı bir
bileşende (`Header`) bir kez yazıldı:

```python
inventory = login_as(Users.STANDARD)
inventory.add_to_cart(Products.BACKPACK)
assert inventory.header.cart_count() == 1
```

**Akıllı bekleme.** Projede hiç `time.sleep()` yok. Her işlem, elementin hazır olmasını
`WebDriverWait` ile bekliyor. Bu sayede testler hem hızlı hem kararlı.

**Çerezle hızlı giriş.** Girişin kendisini test etmeyen testler (sepet, ödeme, sıralama)
formu doldurmak yerine oturum çerezini doğrudan yazarak giriş yapar. Giriş akışı ise
`test_login.py`'de ayrıca ve eksiksiz test edilir.

**Veri odaklı test.** `@pytest.mark.parametrize` ile tek bir test farklı verilerle defalarca
çalışır (ör. 8 farklı hatalı giriş, 6 ürünün her biri için detay sayfası kontrolü).

**Rastgele test verisi.** Faker ile her çalıştırmada farklı Türkçe isimler ve rezervasyonlar
üretilir. Testler tek bir veri setine bağımlı kalmaz; Türkçe karakterler de test edilmiş olur.

**Temizlik.** API testlerinde oluşturulan her kayıt, test kalsa bile sonunda silinir.

**Fixture'lar.** Tarayıcıyı açıp kapatma, giriş yapma, token alma, test kaydı oluşturma gibi
hazırlıklar fixture'larda; testler sadece kontrol ettikleri şeye odaklanır.

**Hata ayıklamayı kolaylaştıran raporlar.** Kalan UI testlerinin ekran görüntüsü ve sayfa adresi,
her API isteğinin gövdesi, cevabı ve süresi rapora otomatik eklenir. Sayfa işlemleri
(`@allure.step`) raporda adım adım görünür.

## Kurulum ve çalıştırma

Gereksinimler: Python 3.11+, Google Chrome (Firefox testleri için Firefox).

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

```bash
pytest                          # tüm testler
pytest -n auto                  # tüm testler, işlemci sayısı kadar paralel (çok daha hızlı)
pytest -m api                   # sadece API testleri
pytest -m ui                    # sadece web testleri
pytest -m smoke                 # sadece kritik akışlar
pytest -m known_bug             # sadece bilinen hataları belgeleyen testler
pytest -m ui --browser firefox  # web testlerini Firefox'ta çalıştır
pytest -m ui --headed           # tarayıcıyı görerek çalıştır
pytest tests/ui/test_cart.py    # tek bir dosya
pytest -k checkout              # adında "checkout" geçen testler
```

### Raporlar

- **HTML rapor:** her çalıştırmadan sonra `reports/report.html` (tarayıcıda aç).
- **Allure raporu:** sonuçlar `reports/allure-results` klasörüne yazılır. Görüntülemek için
  ([Allure CLI](https://allurereport.org/docs/install/) gerekir):

  ```bash
  allure serve reports/allure-results
  ```

### Ayarlar (ortam değişkenleri)

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `BASE_URL` | `https://www.saucedemo.com` | Web testlerinin hedefi |
| `API_BASE_URL` | `https://restful-booker.herokuapp.com` | API testlerinin hedefi |
| `BROWSER` | `chrome` | `chrome` veya `firefox` (`--browser` ile de verilebilir) |
| `HEADLESS` | `true` | `false` yapılırsa tarayıcı görünür açılır (`--headed` ile aynı) |
| `EXPLICIT_WAIT` | `10` | Element bekleme süresi (saniye) |
| `API_MAX_RESPONSE_TIME` | `5` | API cevap süresi sınırı (saniye) |
| `BROWSER_BINARY` / `DRIVER_PATH` | boş | Boşsa Selenium Manager tarayıcıyı ve sürücüyü kendisi bulur |

### Kod stili

```bash
ruff check .          # hata denetimi
ruff format .         # otomatik biçimlendirme
```

## CI (GitHub Actions)

```
lint ──┐
api ───┼──► Allure raporu ──► GitHub Pages
ui (chrome) ──┤
ui (firefox) ─┘
```

- **Ne zaman çalışır:** `main` dalına her push'ta, her pull request'te, her gece 06:17'de
  (Türkiye saati) ve **Actions → Testler → Run workflow** butonuyla elle.
- **İşler:** kod stili denetimi, API testleri ve iki tarayıcıda UI testleri paralel çalışır.
  Ağ kaynaklı geçici hatalara karşı kalan testler otomatik olarak yeniden denenir.
- **Raporlar:** her çalıştırmanın altında HTML raporlar, ekran görüntüleri ve birleşik Allure
  raporu indirilebilir dosya (artifact) olarak bulunur.
- **Canlı rapor:** `main` dalındaki her çalıştırmadan sonra birleşik Allure raporu GitHub Pages'te
  yayınlanır: https://yigitdelen.github.io/test-automation/
