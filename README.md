# TiviATV FHD

TiviMate düzeninde, 1920×1080 openATV / enigma2 skini.
Yuvarlak köşeler, gradientler, ilerleme çubukları ve seçim vurgusu — hepsi
enigma2'nin kendi çizim motoruyla, **tek bir PNG kullanılmadan**.

![önizleme](TiviAtv-FHD/preview.png)

## İki sürüm

| | `TiviAtv-FHD` | `TiviAtv-FHD-PNG` |
|---|---|---|
| Gereken openATV | **7.3+** | **her sürüm** (7.0 dahil) |
| Yuvarlaklık / gradient | motor çiziyor | 43 PNG'ye pişirilmiş (52 KB) |
| OpenSkin Designer'da | köşeler kare görünür | doğru görünür |
| Renk teması değiştirmek | `<colors>` bloğu, tek satır | PNG'lerin yeniden üretimi gerekir |

`cornerRadius`, gradient ve `itemCornerRadiusSelected` enigma2 motoruna
**7.3 ile** girdi — openATV'nin 7.2 ve altındaki dallarında bu tanımlar yok.
Kutun eskiyse ya da tasarımcıda çalışacaksan PNG sürümünü kullan.

## Kurulum

Klasörü olduğu gibi kutuya kopyala:

```
/usr/share/enigma2/TiviAtv-FHD/
```

Sonra: **Menü → Ayarlar → Sistem → Kullanıcı arayüzü → Skin seçimi**

TiviMate görünümü için kanal listesini iki satırlı moda al —
**Menü → Ayarlar → Kanal seçimi**:

- "İki satırlı servis listesi" = **Evet**
- "Sayfa başına öğe" = **10**

> Kanal listesi satır yüksekliği skinden gelmez. enigma2 bunu
> `liste yüksekliği ÷ sayfa başına öğe` olarak hesaplar
> (`ServiceList.setItemsPerPage`), yani `serviceItemHeight` bu hesabın altında
> kalır. Satırlar sık ya da seyrek görünüyorsa o ayarı değiştir.

## Tanımlı ekranlar

`InfoBar` · `SecondInfoBar` · `ChannelSelection` · `SimpleChannelSelection` ·
`ChannelSelectionRadio` · `EPGSelection` · `GraphMultiEPG` · `GraphMultiEPGList` ·
`EventView` · `Menu` · `Setup` · `MessageBox` · `ChoiceBox` · `Volume` · `Mute` ·
`NumberZap` · `SimpleSummary`

Burada tanımlı olmayan ekranlar openATV'nin kendi `skin_default.xml`'inden gelir,
yani hiçbir ekran boş kalmaz.

## Özelleştirme

### Renkler

Tek yerden değişir — `TiviAtv-FHD/skin.xml` başındaki `<colors>` bloğu.

> **Alfa terstir.** Format `#AARRGGBB` ama `AA` = *şeffaflık*:
> `00` tamamen opak, `FF` tamamen görünmez. CSS'ten alışkın olanın en sık
> düştüğü tuzak.

Virgül içeren her `<color>` değeri otomatik olarak **gradient** sayılır:

```xml
<color name="cardGrad" value="#001c1c24,#00141419,vertical" />
```

Sözdizimi: `başlangıç[,orta],bitiş,vertical|horizontal[,alphaBlend]`

### Yuvarlak köşeler

```xml
cornerRadius="24"                   <!-- dört köşe -->
cornerRadius="3;left"               <!-- sadece sol -->
cornerRadius="30;topLeft,topRight"  <!-- seçili köşeler -->
```

Geçerli köşe adları: `topLeft` `topRight` `top` `bottomLeft` `bottomRight`
`bottom` `left` `right`

### Font

Dört `.ttf` dosyasını değiştir, `<fonts>` bloğundaki adları güncelle.
Font adları (`TM` / `TMM` / `TMB` / `TMX`) aynı kalırsa başka hiçbir şey değişmez.

## Araçlar

Depo kökünden çalıştırılır, hiçbirinde sabit yol yok.

| Betik | Ne yapar |
|---|---|
| `tools/lint_skin.py` | Skini openATV'nin **gerçek** attribute listesine karşı denetler — `skin.py` ve `ServiceList.py`'yi upstream'den indirip parse eder. Tanımsız renk/font, ekran dışına taşan eleman, bilinmeyen attribute yakalar. |
| `tools/make_png_variant.py` | PNG sürümünü üretir. `cornerRadius` + `backgroundColor` taşıyan her elemanı bulur, **tam o boyutta** yuvarlak köşeli + gradientli bir PNG çizer, arkasına `<ePixmap alphatest="blend">` koyar. Esnetme yok, alfa korunur. |
| `tools/render_preview.py` | `preview.html`'i üretir — ekranları skin.xml'in gerçek koordinat, renk ve yarıçaplarından tarayıcıda çizer. |
| `tools/make_thumb.py` | Skin seçicideki `preview.png`'yi üretir. |
| `tools/make_designer_copy.py` | OpenSkin Designer uyumlu kopya üretir (aşağıya bak). |

Gereksinim: Python 3.9+ ve `Pillow` (yalnız PNG üreten iki betik için).

```bash
pip install pillow
```

## OpenSkin Designer notları

[OpenSkin Designer](https://github.com/iMaxxx/OpenSkin-Designer) 2014'ten ve
skini olduğu gibi açamaz. `tools/make_designer_copy.py` uyumlu bir kopya üretir:

| Sorun | Neden | Kopyada |
|---|---|---|
| `<alias>` | `cDataBase.initFonts` `<fonts>` altındaki **her** çocuk düğümden `filename` okuyor, düğüm adı filtresi yok → `NullReferenceException` | kaldırılır |
| Blok içi XML yorumları | Yorum düğümünde hiç attribute yok, aynı çökme | kaldırılır |
| Gradient renk değerleri | `#a,#b,vertical` renk olarak ayrıştırılamaz | iki durağın ortalaması alınır |
| `<windowstyle>` içindeki `listbox`/`label`/`configList`/`scrolllabel` | Çalışan örnek skinlerde yok, `name` attribute'u yok | kaldırılır |

`cornerRadius` string'i programın binary'sinde hiç geçmiyor — bu yüzden sıfır-PNG
sürümü tasarımcıda **her zaman kare köşeli** görünür. PNG sürümünü aç.

```bash
python tools/make_designer_copy.py --png
```

## Lisans

Skin dosyaları MIT ile — bkz. [LICENSE](LICENSE).
Barlow fontu SIL Open Font License 1.1 altındadır, ayrıntılar `OFL-Barlow.txt`.
Kanal logoları (picon) skine dahil değildir; ayrı paket olarak
`/usr/share/enigma2/picon/` altına kurulur.

---

## In English

A TiviMate-style 1080p skin for openATV / enigma2. Rounded corners, gradients,
progress bars and selection highlights are drawn by the enigma2 engine itself —
**no PNG assets at all**.

Two variants: `TiviAtv-FHD` needs openATV **7.3+** (that is when `cornerRadius`,
gradients and `itemCornerRadiusSelected` landed in the engine);
`TiviAtv-FHD-PNG` bakes the same look into 43 exactly-sized PNGs (52 KB) and
works on **any** version, including inside OpenSkin Designer.

Copy the folder to `/usr/share/enigma2/`, pick it under
**Menu → Setup → System → User interface → Skin**, and enable the two-line
service list for the TiviMate layout.

The `tools/` scripts regenerate everything from `skin.xml`; the PNG variant is
generated, never hand-edited.
