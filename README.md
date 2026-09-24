# psikolojikansiklopedi — Otomatik Instagram Yayınlama Sistemi

Bu sistem, `content_queue/queue.json` içine eklediğiniz gönderileri her gün otomatik olarak
Instagram hesabınıza yükler. Kurulum tek seferlik, sonrasında sadece içerik eklemeniz yeterli.

---

## 1) Tek seferlik kurulum (yaklaşık 20-30 dakika)

### A. Instagram hesabını Professional hesaba çevirin
Instagram uygulaması → Profil → Menü (≡) → Ayarlar → Hesap türü ve araçlar →
"Profesyonel hesaba geç" → **Creator** veya **Business** seçin.

### B. Facebook Sayfası bağlayın
Aynı ekranda "Facebook'a bağlan" seçeneğiyle bir Facebook Sayfası oluşturun/bağlayın.
Instagram Graph API, izinleri bu sayfa üzerinden çalıştırır — sayfa olmadan API çalışmaz.

### C. Meta Developer uygulaması oluşturun
1. https://developers.facebook.com adresine gidip Facebook hesabınızla giriş yapın.
2. "My Apps" → "Create App" → tür olarak **Business** seçin.
3. Uygulama panelinde "Add Product" → **Instagram Graph API**'yi ekleyin.

### D. Kendinizi test kullanıcısı yapın (App Review'a gerek kalmadan)
1. Uygulama panelinde Instagram ürünü ayarlarına girin.
2. "Roles" → "Instagram Testers" bölümünden kendi Instagram kullanıcı adınızı ekleyin.
3. Instagram uygulamasından (Ayarlar → Uygulamalar ve Websiteler → Tester Davetleri)
   daveti kabul edin.
   
   *(Sadece kendi hesabınıza paylaşım yapacağınız için bu adım yeterli — Meta'nın
   haftalar süren app review sürecine girmenize gerek yok.)*

### E. Erişim token'ı ve kullanıcı ID'sini alın
1. https://developers.facebook.com/tools/explorer adresine gidin, uygulamanızı seçin.
2. Sağ üstten izinleri seçin: `instagram_business_basic`, `instagram_business_content_publish`,
   `pages_show_list`, `pages_read_engagement`.
3. "Generate Access Token" ile kısa ömürlü bir token alın.
4. Bu token'ı [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
   ile **uzun ömürlü token'a** (60 gün) çevirin.
5. Graph API Explorer'da `GET /me/accounts` isteğiyle Facebook Sayfa ID'nizi,
   ardından `GET /{page-id}?fields=instagram_business_account` isteğiyle
   Instagram User ID'nizi bulun.

⚠️ **Önemli:** Token 60 günde bir sona erer. Süresi dolmadan birkaç gün önce
adım E'yi tekrarlayıp GitHub Secret'ını güncellemeniz gerekir. Bunu takvime
not almanızı öneririm.

### F. Bu projeyi GitHub'a yükleyin
1. GitHub'da yeni bir **private** repo oluşturun (örn. `ig-autopost`).
2. Bu klasördeki tüm dosyaları o repoya push edin.

### G. Token'ları GitHub Secrets'a ekleyin
Repo → Settings → Secrets and variables → Actions → "New repository secret":
- `IG_ACCESS_TOKEN` → D adımında aldığınız uzun ömürlü token
- `IG_USER_ID` → Instagram User ID'niz

---

## 2) Günlük kullanım — içerik eklemek

`content_queue/queue.json` dosyasına yeni bir gönderi eklemeniz yeterli:

```json
{
  "id": "2026-10-01-ornek",
  "image_path": "content_queue/images/2026-10-01-ornek.jpg",
  "caption": "Gönderi metni buraya... #psikoloji",
  "posted": false
}
```

Görseli de `content_queue/images/` klasörüne aynı isimle ekleyip repoya push edin.
Sistem her gün sıradaki `"posted": false` olan ilk gönderiyi otomatik yayınlar ve
yayınladıktan sonra `"posted": true` yapıp kendi kendine kaydeder.

**Öneri:** Bana her hafta o haftanın konularını söylerseniz, caption metinlerini ve
görselleri ben hazırlarım; siz sadece queue.json'a eklersiniz.

---

## 3) Saat / sıklık değiştirme

`.github/workflows/daily-post.yml` içindeki `cron: "0 7 * * *"` satırını değiştirin.
Saatler **UTC**'dir — Türkiye saatinden 3 saat geridir (örn. TR 10:00 → UTC 07:00).

---

## 4) Test etme

Kurulumu yaptıktan sonra beklemeden test etmek için:
Repo → Actions sekmesi → "Günlük Instagram Gönderisi" → "Run workflow" butonuyla
elle bir kez tetikleyebilirsiniz.
