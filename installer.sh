#!/bin/sh
# TiviATV FHD kurulumu (openATV / enigma2 kutusunda, telnet ya da SSH ile):
#
#   wget -qO- https://raw.githubusercontent.com/fyildirim-debug/tiviatv-fhd/main/installer.sh | sh
#
# Depodaki son paketi (dist/) indirir, sha256 ile dogrular ve opkg ile kurar.
# Kuruluysa ayni komut gunceller; yazi tipi secimi (fonts.xml) korunur.
# Kaldirmak: opkg remove enigma2-plugin-skins-tiviatv-fhd

RAW="${TIVIATV_RAW:-https://raw.githubusercontent.com/fyildirim-debug/tiviatv-fhd/main}"  # test: TIVIATV_RAW=http://...
PKG="enigma2-plugin-skins-tiviatv-fhd"
TMP="/tmp/tiviatv-fhd.$$"

fail() {
	echo "HATA: $*"
	rm -rf "$TMP"
	exit 1
}

command -v opkg >/dev/null 2>&1 || fail "opkg bulunamadi; bu betik enigma2 kutusunda calisir."

VER=$(wget -qO- "$RAW/VERSION" | tr -d ' \r\n')
[ -n "$VER" ] || fail "surum okunamadi (internet baglantisi?)"
IPK="${PKG}_${VER}_all.ipk"

mkdir -p "$TMP" || fail "$TMP olusturulamadi"
echo "TiviATV FHD $VER indiriliyor..."
wget -qO "$TMP/$IPK" "$RAW/dist/$IPK" || fail "paket indirilemedi"
wget -qO "$TMP/$IPK.sha256" "$RAW/dist/$IPK.sha256" || fail "sha256 indirilemedi"
if command -v sha256sum >/dev/null 2>&1; then
	(cd "$TMP" && sha256sum -c "$IPK.sha256" >/dev/null 2>&1) || fail "paket bozuk indi (sha256 tutmadi)"
fi

# ayni surum kuruluysa da yeniden kur (bozuk kurulumu onarir)
opkg install --force-reinstall "$TMP/$IPK" || fail "opkg kurulumu basarisiz"
rm -rf "$TMP"

if grep -q "^config.skin.primary_skin=TiviAtv-FHD/" /etc/enigma2/settings 2>/dev/null; then
	echo "Skin etkin: degisiklikler icin arayuzu yeniden baslatin (Menu > Bekleme / Yeniden Baslat > Kullanici Arayuzunu Yeniden Baslat)."
fi
exit 0
