#!/bin/sh
# TiviATV FHD installer (run on the openATV / enigma2 box over telnet or SSH):
#
#   wget -qO- https://raw.githubusercontent.com/fyildirim-debug/tiviatv-fhd/main/installer.sh | sh
#
# Downloads the latest package from dist/, verifies its sha256 and installs it
# with opkg. Run it again to update; your font choice (fonts.xml) is kept.
# Remove: opkg remove enigma2-plugin-skins-tiviatv-fhd

RAW="${TIVIATV_RAW:-https://raw.githubusercontent.com/fyildirim-debug/tiviatv-fhd/main}"  # test: TIVIATV_RAW=http://...
PKG="enigma2-plugin-skins-tiviatv-fhd"
TMP="/tmp/tiviatv-fhd.$$"

fail() {
	echo "ERROR: $*"
	rm -rf "$TMP"
	exit 1
}

command -v opkg >/dev/null 2>&1 || fail "opkg not found; run this on the enigma2 box."

VER=$(wget -qO- "$RAW/VERSION" | tr -d ' \r\n')
[ -n "$VER" ] || fail "could not read the version (internet connection?)"
IPK="${PKG}_${VER}_all.ipk"

mkdir -p "$TMP" || fail "could not create $TMP"
echo "Downloading TiviATV FHD $VER..."
wget -qO "$TMP/$IPK" "$RAW/dist/$IPK" || fail "could not download the package"
wget -qO "$TMP/$IPK.sha256" "$RAW/dist/$IPK.sha256" || fail "could not download the sha256 file"
if command -v sha256sum >/dev/null 2>&1; then
	(cd "$TMP" && sha256sum -c "$IPK.sha256" >/dev/null 2>&1) || fail "the package is corrupt (sha256 mismatch)"
fi

# reinstall even if this version is installed (repairs a broken install)
opkg install --force-reinstall "$TMP/$IPK" || fail "opkg install failed"
rm -rf "$TMP"

if grep -q "^config.skin.primary_skin=TiviAtv-FHD/" /etc/enigma2/settings 2>/dev/null; then
	echo "The skin is active: restart the GUI to load the new version (Menu > Standby / Restart > Restart GUI)."
fi
exit 0
