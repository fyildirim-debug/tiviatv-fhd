# TiviATV FHD

TiviMate düzeninde ve görünümünde, 1920×1080 openATV / enigma2 skini.
Yayın arkada akarken yarı saydam paneller, beyaz seçim hapları, yuvarlak
köşeler, ince ilerleme çizgileri ve Inter yazı tipi — hepsi enigma2'nin kendi
çizim motoruyla, **tek bir PNG kullanılmadan**.

![TiviATV FHD: kanal listesi, program rehberi, InfoBar, çoklu EPG](docs/screenshots/hero.jpg)

**English:** [README.md](README.md) · [Kurulum](#kurulum) · [Ekranlar](#ekranlar)

## Gereksinim

openATV **7.3+**. `cornerRadius`, gradient ve `itemCornerRadiusSelected`
enigma2 motoruna 7.3 ile girdi; 7.2 ve altındaki dallarda bu tanımlar yok,
köşeler kare çıkar.

## Kurulum

1. **Kutuya bağlan.** Bilgisayardan telnet ya da SSH ile (`ssh root@<kutu-ip>`).
   Kutunun IP adresi ağ ayarlarında yazar.
2. **Kur.** Şu komutu yapıştır:

   ```sh
   wget -qO- https://raw.githubusercontent.com/fyildirim-debug/tiviatv-fhd/main/installer.sh | sh
   ```

   Betik son paketi indirir, sha256 ile doğrular ve `opkg` ile kurar.
3. **Skini seç.** **Menü → Kurulum → Kullanım & Kullanıcı Arayüzü → Arayüz
   Ayarları** → `TiviAtv-FHD`, **YEŞİL** tuşla etkinleştir; arayüz yeniden başlar.
4. **Kanal listesini TiviMate düzenine al.** **Menü → Kurulum → Kullanım &
   Kullanıcı Arayüzü → Kanal Seçim Ayarları**:
   - "Kanal listesinde her giriş için iki satır göster" = **Evet**
   - "Kanal listesi satır sayısı" = **10**

   Satır yüksekliği skinden değil bu sayıdan gelir (liste yüksekliği ÷ satır
   sayısı); satırlar sık ya da seyrek görünürse sayıyı değiştir.
5. **Yazı tipi (isteğe bağlı).** Aynı menüde **TiviATV Yazı Tipi** (İngilizce arayüzde *TiviATV Font*): Inter
   (varsayılan), Geist, Barlow ya da kutudaki başka bir font.

**Güncellemek:** aynı komutu yeniden çalıştır. Yazı tipi seçimin korunur.

**Dil:** skinin yazıları (NOW, NEXT, LATER), ekran başlıkları ve yazı tipi
seçici İngilizcedir; kutunun arayüz dili Türkçeyse enigma2'nin çevirisiyle
NOW / NEXT, ŞİMDİ / SONRA olarak görünür; yazı tipi seçici ve sinyal yüzdeleri de
Türkçeleşir.

**Kaldırmak:**

```sh
opkg remove enigma2-plugin-skins-tiviatv-fhd
```

**İnternetsiz / elle:** [`dist/`](dist/) altındaki `.ipk`'yi FTP ya da SCP ile
kutunun `/tmp` klasörüne at, sonra:

```sh
opkg install /tmp/enigma2-plugin-skins-tiviatv-fhd_*_all.ipk
```

**Paketsiz:** `TiviAtv-FHD/` klasörünü `/usr/share/enigma2/` altına,
`TiviAtv-FHD/converter/*.py` dosyalarını converter dizinine,
`plugin/TiviAtvFont/` klasörünü eklenti dizinine kopyala. Converter'lar
kopyalanmazsa skin yine açılır, yalnız sinyal, rozet ve softcam (ECM) alanları
boş kalır.

### Paket içeriği

`enigma2-plugin-skins-tiviatv-fhd` üç yere kurar:

| Yer | İçerik |
|---|---|
| `/usr/share/enigma2/TiviAtv-FHD/` | skin, `fonts.xml`, yazı tipleri, lisanslar, önizleme |
| `/usr/lib/enigma2/python/Components/Converter/` | `TiviAtvSignal.py`, `TiviAtvText.py`, `TiviAtvEcm.py` |
| `/usr/lib/enigma2/python/Plugins/Extensions/TiviAtvFont/` | yazı tipi seçici |

| Converter | Ne yapar |
|---|---|
| `TiviAtvSignal.py` | Sinyal (SNR/AGC) ya da IPTV akış hızı |
| `TiviAtvText.py` | Çözünürlük / codec / şifre rozetlerini boşken gizler |
| `TiviAtvEcm.py` | `/tmp/ecm.info`'dan softcam ECM bilgisi (OSCam, CCcam …), yalnız şifreli kanalda — bkz. [Softcam (ECM) bilgisi](#softcam-ecm-bilgisi) |

`fonts.xml` paketin yapılandırma dosyasıdır: değiştirdiysen opkg onu ezmez,
kurulum betiği yeni sürümün şablonunu alıp senin seçtiğin dört font satırını
içine koyar (yeni eklenen font tanımları eksik kalmasın diye).

## Ekranlar

Görüntüler PC emülatöründen (örnek kanal listesi, EPG ve picon ile, bkz.
[Emülatörde test](#emülatörde-test)). Emülatörde video oynamadığı için OSD,
kutudaki donanım birleştirmesi gibi alfasıyla örnek bir yayın karesinin üstüne
konuldu (kare: Unsplash, Vienna Reyes).

### InfoBar

Yayından koyuya solan alt bant, ince kenarlı logo karosu, numara çipi + kanal,
program, kalan süre ve boşken gizlenen rozetler. Süre çizgisi başlangıç ve bitiş
saatinin arasında 4 px'lik ince bir hat: dolgu sönük arduvazdan parlak beyaza
akar, ucu hep en parlak yer. Sağ
altta uydu kanalında SNR/AGC yüzdeleri, IPTV'de akış hızı — ikisi de aynı alanı
paylaşır, hangi kaynak aktifse o görünür.

![InfoBar](docs/screenshots/infobar.jpg)

Şifreli kanalda sonraki program satırının sağında softcam'in neyle açtığı
görünür: sistem ve CAID, okuyucu, protokol, hop ve ECM süresi (bkz.
[Softcam (ECM) bilgisi](#softcam-ecm-bilgisi)).

![OSCam ECM bilgili InfoBar](docs/screenshots/infobar-ecm.jpg)

İkinci bilgi çubuğu (InfoBar açıkken OK): programın tam açıklaması ve türü.

![İkinci bilgi çubuğu](docs/screenshots/second-infobar.jpg)

### Kanal listesi

TiviMate'teki gibi yayın durmadan tam ekran arkada akar (PiG kutusu yok):
solda yarı saydam panelde iki satırlı liste, picon ve ilerleme; seçili kanal
gri odakla (beyaz hap beyaz logoları yutardı). Sağ altta seçili kanalın
şimdi/sonraki kartı, sağ üstte saat.

![Kanal listesi](docs/screenshots/channelselection.jpg)

### Program rehberi

Zaman çizelgesi: yarı saydam zemin, TiviMate gibi gri hücreler; şu an yayında
olanlar bir ton açık, seçili hücre açık gri, kırmızı "şimdi" çizgisi, izlenen
kanalın adı mavi. Renkler ve font motorun EPG listesine skin attribute'larıyla
verilir (önceden motorun varsayılan yeşil/sarı bloklarıydı).

![EPG](docs/screenshots/epg-grid.jpg)

Çoklu EPG: Şimdi / Sonraki / Daha sonra sekmeleri ve seçili programın kartı.

![Çoklu EPG](docs/screenshots/epg-multi.jpg)

Tek kanal EPG ve program detayı (benzer yayınlarla).

<table>
<tr>
<td width="50%"><img src="docs/screenshots/epg-single.jpg" alt="Tek kanal EPG"></td>
<td width="50%"><img src="docs/screenshots/event-view.jpg" alt="Program detayı"></td>
</tr>
</table>

### Kanal menüsü

Kanal listesinde MENU: sağdan açılan çekmece.

![Kanal menüsü](docs/screenshots/channel-menu.jpg)

### Sanal klavye

Alttan açılan sayfa; tuşlar PNG değil, motorun çizdiği kutular ve ikon fontu.

![Klavye](docs/screenshots/keyboard.jpg)

### Menü

Yayın üstünde sağa doğru solan yarı saydam sol panel, beyaz seçim hapı.

![Menü](docs/screenshots/menu.jpg)

### Ayarlar

![Ayarlar](docs/screenshots/setup.jpg)

### Zamanlayıcılar

Kayıt listesi beyaz seçim hapıyla; sağda seçili programın kartı.

![Zamanlayıcılar](docs/screenshots/timers.jpg)

### Eklentiler

Izgara düzeninde eklenti tarayıcı, altta renk tuşu çipleri.

![Eklentiler](docs/screenshots/plugins.jpg)

### Ses

Altta ince kenarlı hap: hoparlör glifi (`enigma2icons`), ince süre çizgisiyle
aynı dolgu, sayı. Sessizde yalnız kırmızı, üstü çizili hoparlör simgesi olan
yuvarlak çip; yazı yok, her dilde aynı okunur.

![Ses](docs/screenshots/volume.jpg)

### Numara ile kanal

Numara kendi karosunda, kanal adı yanında. Kullanım ayarlarında numara zap
logosu açıksa picon sağda çerçevesiz görünür (motor o zaman `NumberZapPicon`
adını arar, aynı tasarım o adla da tanımlı).

![Numara zap](docs/screenshots/numberzap.jpg)

### Oynatıcı

Geçen / kalan süre ince çizginin iki ucunda; duraklatınca sol üstte durum hapı
(`PVRState`).

![Oynatıcı](docs/screenshots/player.jpg)

### Renk tuşları

Doygun renkli haplar yerine koyu cam çip + renkli nokta + beyaz yazı. Nokta,
tuşla aynı kaynağa bağlı ayrı bir etiket; tuş boşken ikisi birlikte gizlenir.
(Görüntülerdeki alt satırlar.)

### Yazı tipleri

Aynı InfoBar dört yazı tipiyle. Varsayılan Inter; diğerleri **TiviATV Yazı
Tipi** eklentisinden seçilir (bkz. [Font](#font)).

![Yazı tipleri](docs/screenshots/fonts.jpg)

### Diğer ekranlar

<table>
<tr>
<td width="50%"><img src="docs/screenshots/messagebox.jpg" alt="Onay kutusu"><br>Onay kutusu</td>
<td width="50%"><img src="docs/screenshots/inputbox.jpg" alt="Giriş kutusu"><br>Giriş kutusu</td>
</tr>
<tr>
<td><img src="docs/screenshots/pin.jpg" alt="PIN"><br>Ebeveyn kilidi PIN</td>
<td><img src="docs/screenshots/mute.jpg" alt="Sessiz"><br>Sessiz</td>
</tr>
<tr>
<td><img src="docs/screenshots/console.jpg" alt="Konsol"><br>Konsol (paket kurulumu)</td>
<td><img src="docs/screenshots/information.jpg" alt="Bilgi"><br>İmaj bilgisi</td>
</tr>
<tr>
<td><img src="docs/screenshots/skin-settings.jpg" alt="Arayüz ayarları"><br>Arayüz ayarları (skin seçimi)</td>
<td><img src="docs/screenshots/font-picker.jpg" alt="Yazı tipi seçici"><br>Yazı tipi seçici</td>
</tr>
<tr>
<td><img src="docs/screenshots/hotkey-settings.jpg" alt="Kısayol tuşları"><br>Kısayol tuşu ayarları</td>
<td><img src="docs/screenshots/hotkey-functions.jpg" alt="Kısayol işlevleri"><br>Kısayol tuşu ayarları: işlev seçimi</td>
</tr>
<tr>
<td><img src="docs/screenshots/input-devices.jpg" alt="Giriş aygıtları"><br>Giriş aygıtları</td>
<td><img src="docs/screenshots/locale.jpg" alt="Dil / bölge"><br>Dil / bölge</td>
</tr>
</table>

## Tanımlı ekranlar

`InfoBar` · `SecondInfoBar` · `ChannelSelection` · `SimpleChannelSelection` ·
`ChannelSelectionRadio` · `EPGSelection` · `GraphicalEPG` · `GraphicalEPGPIG` ·
`EPGSelectionMulti` · `GraphMultiEPG` · `GraphMultiEPGList` · `EventView` ·
`Menu` · `Setup` · `MessageBox` · `ChoiceBox` · `Volume` ·
`Mute` · `NumberZap` · `NumberZapPicon` · `AudioSelection` · `SkinSelection` · `PluginBrowser` ·
`PackageAction` · `ChannelContextMenu` · `InputBox` · `PinInput` · `PinInputPopup` ·
`VirtualKeyBoard` · `Console` · `TextBox` · `Information` · `TimerEditList` ·
`MoviePlayer` · `PVRState` · `ButtonSetup` · `ButtonSetupSelect` · `InputDeviceSelection` ·
`LocaleSelection` · `SimpleSummary`

Ayrıca enigma2'nin standart renk adları (`window-bg`, `window-fg`, `key_red`,
`grey` …) skin paletine eşlendi. Bunlar tanımsızken, skinde karşılığı olmayan
her ekran — üçüncü taraf eklentiler dahil — `parseColor` hatasına düşüp
okunaksız kalıyordu.

> EPG ekranlarının adı openATV 8 ile değişti: `GraphMultiEPG` yerine
> `GraphicalEPG` / `GraphicalEPGPIG` / `EPGSelectionMulti` aranıyor. Eski adlar
> 7.3–7.5 dalları için duruyor.

Burada tanımlı olmayan ekranlar openATV'nin kendi `skin_default.xml`'inden gelir,
yani hiçbir ekran boş kalmaz.

> `MessageBox` için `icon` widget'ı zorunlu: openATV'nin `skin.py`'si
> (`MANDATORY_WIDGETS`) eksik widget'lı ekranı reddedip varsayılan pencereyi
> açıyor. Yeni ekran eklerken bu listeye bak.

### PNG'siz motor kontrolleri

openATV 2026-09 itibarıyla bazı kontrolleri PNG yerine kendisi çizebiliyor;
skin bunları `<parameters>` bloğundan açar:

| Parametre / attribute | Etkisi |
|---|---|
| `EPGNativeControls` | Grafik EPG'deki "şimdi" çizgisi ve zaman çizgileri, çoklu EPG sekmeleri renkli etiket olur |
| `VirtualKeyboardNative` | Sanal klavye tuşları yuvarlak köşeli kutu + `enigma2icons` glifi |
| `ChoiceListNative` | ChoiceBox / kanal menüsü satırlarındaki numara ve madde ikonları |
| `iconFont` / `iconGlyphs` | MessageBox ve oynatıcı durum ikonları font glifinden |

Daha eski imajlar bu parametreleri yok sayar: tuşlar ve ikonlar
`skin_default` grafikleriyle çizilir, zaman çizgileri için iki tanım
`objectTypes` ile seçilir (Label ise renkli çizgi, Pixmap ise eski PNG).

## Özelleştirme

### Renkler

Tek yerden değişir — `TiviAtv-FHD/skin.xml` başındaki `<colors>` bloğu.

> **Alfa terstir.** Format `#AARRGGBB` ama `AA` = *şeffaflık*:
> `00` tamamen opak, `FF` tamamen görünmez. CSS'ten alışkın olanın en sık
> düştüğü tuzak.

Gradient, `<colors>` bloğunda **tanımlanamaz** — `parseColor` orada yalnız
`#aarrggbb` kabul eder, virgüllü değer sessizce beyaza düşer. Gradient doğrudan
elemanın attribute'una yazılır; `backgroundColor` / `foregroundColor` değerinde
virgül görürse `parseGradient`'e gider:

```xml
<eLabel backgroundColor="#001c1c24,#00141419,vertical" />
```

Sözdizimi: `başlangıç[,orta],bitiş,vertical|horizontal[,alphaBlend]`

### Saydamlık

Paneller yayının üstünde **düz yarı saydam dolgu**: enigma2 dolgunun alfasını
piksele olduğu gibi yazar, OSD'yi görüntü katmanıyla birleştirmeyi kutunun
donanımı yapar — ek CPU yükü yok. Gradyanın sonundaki `alphaBlend` (`,1`)
bayrağı ise her pikseli CPU'da alttakiyle karıştırır; grafik hızlandırması
olmayan kutularda (ör. Octagon SX88V2) geniş alanda kullanılmaz. Solmalar
bayraksız gradyandır.

Saydamlık renkleri `<colors>`'ta: `glass` (panel, %80 opak), `glassSoft`
(saat kapsülü), `card` (diyalog / kart), `chip` (rozet), `scrim` (diyalog
arkası karartma). Seçim: `selBg` / `selFg` (beyaz hap), `focus` / `focusHi`
(gri odak). Çizgiler: `track` (ilerleme ve kaydırma çubuğu zemini), `edge`
(kart ve çiplerin 2 px kenarı).

> Kutu kenarı `eLabel`'da `widgetBorderWidth` / `widgetBorderColor` ile
> çizilir. `borderWidth` / `borderColor` orada yazının dış çizgisidir
> (`elabel.h`); `lint_skin.py` bunu uyarır.

> Pencereler üst üste binerken de karıştırma yok: üstteki pencerenin pikseli
> alttakinin yerine geçer. Yarı saydam bir kartın arkasından alttaki ekran
> değil, yayın görünür.

### Softcam (ECM) bilgisi

InfoBar softcam'in ECM bilgisini kendiliğinden gösterir — skinde ayarlanacak bir
şey yok. OSCam (ve çoğu softcam) açtığı kanal için `/tmp/ecm.info` yazar;
`TiviAtvEcm` converter'ı onu saniyede bir, yalnız dosya değişince okur:

```
Irdeto 0604  ·  my_reader  ·  newcamd  ·  1 hop  ·  0.214 s
```

- Yalnız **şifreli** kanalda ve softcam `/tmp/ecm.info`'yu yazmışken görünür;
  şifresiz kanalda o köşe boş kalır.
- **Menü › Kurulum › Kullanım & Kullanıcı Arayüzü › Ekranda Gösterim (OSD)
  Ayarları › Bilgi Çubuğunda şifreleme bilgisini göster** ayarına uyar
  (İngilizce arayüzde *Show crypto info in InfoBar*): `Kapalı` gizler,
  `Tek satır` / `İki satır` gösterir (varsayılan açık; madde *Uzman* kurulum
  seviyesinde listelenir).
- Aynı ekrandaki **Softcam sunucu adını gizle**, kart ağ üzerinden
  paylaşılıyorsa sunucu adresini gizler (`•••`).
- Softcam sistem adını yazmazsa CAID'den bulunur; ECM süresi softcam saniye de
  yazsa milisaniye de yazsa saniye olarak gösterilir.

Widget `InfoBar` ekranında durur (`<convert type="TiviAtvEcm" />`); her etiket
gibi taşınabilir, biçimi değiştirilebilir.

### Yuvarlak köşeler

```xml
cornerRadius="24"                   <!-- dört köşe -->
cornerRadius="3;left"               <!-- sadece sol -->
cornerRadius="30;topLeft,topRight"  <!-- seçili köşeler -->
```

Geçerli köşe adları: `topLeft` `topRight` `top` `bottomLeft` `bottomRight`
`bottom` `left` `right`

### Font

Varsayılan yazı tipi **Inter**: ekran arayüzleri için çizilmiş, iri x-yüksekliği
sayesinde uzaktan okunan, Türkçe karakterleri eksiksiz bir grotesk. Klasörde
dört ağırlık var (Regular / Medium / SemiBold / Bold → `TM` / `TMM` / `TMB` /
`TMX`); değişken fonttan `opsz=22` kesimiyle statik üretildi — metin kesiminin
(14) rahat aralığıyla başlık kesiminin (32) sıkılığı arasında. Seçicide ikinci
modern seçenek **Geist**, ayrıca Barlow ve eski Sony Sketch durur.

Skin ölçüleri dar bir font için kurulduğundan geniş aileler `fonts.xml`'de
küçültülür: Inter `scale="92"`, Geist `scale="94"` (motor punto × scale / 100
uygular). Eklenti bir aile seçerken bu ölçeği kendisi yazar.

Aktif yazı tipi `skin.xml`'de değil, ayrı bir `fonts.xml` dosyasında durur;
`skin.xml` onu `<include filename="fonts.xml" />` ile yükler. Skinde geçen font
adları (`TM` / `TMM` / `TMB` / `TMX`) hiç değişmez, sadece hangi `.ttf`
dosyasına baktıkları değişir.

Kutu üstünden değiştirmek için paketle gelen eklentiyi aç: **Menü → Kurulum →
Kullanım & Kullanıcı Arayüzü → TiviATV Yazı Tipi** altında, skin klasöründeki ve `/usr/share/fonts` altındaki yazı tipleri
listelenir; seçilen aile `fonts.xml`'e yazılır ve arayüz yeniden başlatılır.
Aynı ailenin birden çok ağırlığı varsa (örneğin Inter'in dördü) dört slot
otomatik eşleşir, tek ağırlıklı bir font seçilirse dördü de ona bakar.
`enigma2icons` gibi glif fontları listeye girmez.

![Yazı tipi seçici](docs/screenshots/font-picker.jpg)

Seçim listesi enigma2'nin `ChoiceBox` ekranıdır — görünümü bu skinin
`<screen name="ChoiceBox">` tanımından gelir, eklentinin içinde gömülü skin
yoktur. `fonts.xml` elle de düzenlenebilir.

## Araçlar

Depo kökünden çalıştırılır, hiçbirinde sabit yol yok.

| Betik | Ne yapar |
|---|---|
| `tools/lint_skin.py` | Skini openATV'nin **gerçek** attribute listesine karşı denetler — `skin.py` ve `ServiceList.py`'yi upstream'den indirip parse eder. Tanımsız renk/font, ekran dışına taşan eleman, bilinmeyen attribute, `eLabel`'da kutu kenarı sanılan yazı kenarını yakalar. |
| `tools/render_preview.py` | `preview.html`'i üretir — ekranları skin.xml'in gerçek koordinat, renk ve yarıçaplarından tarayıcıda çizer. |
| `tools/make_thumb.py` | Skin seçicideki `prev.png`'yi emülatörün kanal listesi görüntüsünden üretir. |
| `tools/build_ipk.py` | Kurulum paketini (`dist/*.ipk` + `.sha256`) üretir; önce lint, Python derlemesi ve `fonts.xml` denetimi. Aynı kaynaktan aynı paket çıkar. |
| `tools/make_fonts.py` | Inter ve Geist'in statik ağırlıklarını Google Fonts'taki değişken fonttan üretir (enigma2 değişken fontta ağırlık seçemez). |
| `tools/make_designer_copy.py` | OpenSkin Designer uyumlu kopya üretir (aşağıya bak). |
| `tools/emulator/` | PC emülatöründe skin testi: örnek kanal/EPG, test yayını, tüm ekranların görüntüsü (aşağıya bak). |

Gereksinim: Python 3.9+, `Pillow` (`make_thumb.py`) ve `fonttools`
(`make_fonts.py`).

```bash
pip install pillow fonttools
```

### Sürüm çıkarma

1. `VERSION`'ı artır, değişikliklerle birlikte commit et.
2. `python3 tools/build_ipk.py` → `dist/` altında yeni paket (eskisi silinir).
3. `dist/`'i commit edip `main`'e push et; `installer.sh` sürümü `VERSION`'dan
   okuduğu için kutular bir sonraki çalıştırmada yeni paketi alır.

## Emülatörde test

Kutuya gitmeden, PC'de derlenmiş OpenATV enigma2 (SDL2) üzerinde denenir.
Emülatörün kendisi FY Sinema deposundaki `tools/e2pc/kur.sh` ile kurulur
(`e2-arkaplan`, `e2-tus`, `e2-ekran` oradan gelir); bu klasör üstüne skin
testine özel parçaları ekler:

| Dosya | Ne yapar |
|---|---|
| `TiviAtvTest/` | Yalnız emülatöre kurulan eklenti: `/tmp/e2py.cmd`'deki Python kodunu enigma2'nin içinde çalıştırır, açılışta örnek EPG'yi yükler. Kutuya **kurulmaz**. |
| `e2-py` | Bu eklentiye kod gönderir: `e2-py 'session.open(...)'` |
| `demo_kanallar.py` | 16 kanallık örnek liste (4 Türksat 42E + 12 IPTV), EPG, picon ve test yayını üretir (enigma2 kapalıyken) |
| `e2-yayin` | IPTV kanallarının çaldığı test yayını (`127.0.0.1:8099`, ffmpeg) |
| `ekranlar.py` | Ekranları menüde gezinmeden tek tek açıp görüntüsünü alır |

```bash
ln -sfn $PWD/TiviAtv-FHD /usr/share/enigma2/TiviAtv-FHD
ln -sf  $PWD/TiviAtv-FHD/converter/*.py /usr/lib/enigma2/python/Components/Converter/
ln -sfn $PWD/tools/emulator/TiviAtvTest /usr/lib/enigma2/python/Plugins/Extensions/TiviAtvTest
python3 tools/emulator/demo_kanallar.py && tools/emulator/e2-yayin && e2-arkaplan
python3 tools/emulator/ekranlar.py                 # hepsi  -> .cache/ekranlar/
python3 tools/emulator/ekranlar.py /tmp/ss menu epgselection
python3 tools/emulator/ekranlar.py --kare kare.jpg /tmp/ss    # OSD'yi örnek yayın karesine bindir
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

`cornerRadius` string'i programın binary'sinde hiç geçmiyor — skin tasarımcıda
**her zaman kare köşeli** görünür. Yuvarlaklık yalnız kutuda, enigma2 çizerken
ortaya çıkar.

```bash
python tools/make_designer_copy.py
```

## Sürüm notları

**1.0.2**
- InfoBar'da softcam ECM bilgisi (OSCam, CCcam …), yalnız şifreli kanalda:
  `/tmp/ecm.info`'dan sistem + CAID, okuyucu, protokol, hop ve ECM süresi
  (yeni `TiviAtvEcm` converter'ı). Bkz. [Softcam (ECM) bilgisi](#softcam-ecm-bilgisi).
- Kısayol tuşu ayarları, giriş aygıtları ve dil / bölge ekranları yenilendi:
  diğer ayar ekranları gibi büyük yarı saydam kartlar, renk tuşu çipleri, dil
  listesinde bayraklar ve durum simgeleri.

**1.0.1**
- Kutuda görünen her şey İngilizce: etiketler (NOW, NEXT, LATER), ekran
  başlıkları, yazı tipi seçici (artık **TiviATV Font**), kurulum betiği ve
  paket mesajları. Sessiz göstergesi yalnız simgeli bir çip (çevrilecek yazı
  yok); NOW çipi MAINTENANT gibi uzun çevirilere de yetiyor. Etiketler ve başlıklar enigma2'nin kendi çevirisiyle kutunun
  arayüz diline uyar; yazı tipi seçici ve sinyal yüzdeleri (86% / %86) Türkçe
  arayüzde Türkçeleşir.
- Ekran görüntüleri İngilizce örnek verilerle yeniden çekildi.

**1.0.0**
- Kurulum paketi olarak ilk sürüm: tek komutla kurulum; skin, iki converter ve
  yazı tipi seçiciyi içeren opkg paketi.
- Varsayılan yazı tipi Inter; ayrıca Geist, Barlow ve Sony Sketch.
- İnce süre çizgileri, renk tuşu çipleri, kenarlı kartlar; yarı saydam
  panellerle TiviMate düzeni.

## Lisans

Skin dosyaları MIT ile — bkz. [LICENSE](LICENSE).
Inter, Geist ve Barlow fontları SIL Open Font License 1.1 altındadır, ayrıntılar
`OFL-Inter.txt`, `OFL-Geist.txt`, `OFL-Barlow.txt`. Inter ve Geist'in statik
ağırlıkları Google Fonts'taki değişken fonttan `fontTools` ile üretildi (OFL
değiştirilmiş sürüme izin verir; iki ailede de ayrılmış font adı yok).
`Sony_Sketch_Bold_205.ttf` üçüncü taraf bir fonttur; dağıtım hakları skin
lisansının kapsamı dışındadır.
Kanal logoları (picon) skine dahil değildir; ayrı paket olarak
`/usr/share/enigma2/picon/` altına kurulur.
