# TiviATV FHD kurulum paketi (.ipk) uretir: skin, converter'lar ve yazi tipi
# eklentisi tek pakette. Surum depo kokundeki VERSION dosyasindan okunur.
# Cikti: dist/<paket>_<surum>_all.ipk (+ .sha256); eski surumun dosyalari silinir.
#
#   python3 tools/build_ipk.py
#
# Paketlemeden once lint_skin.py, Python derlemesi ve fonts.xml'in baktigi
# dosyalar denetlenir; biri kalirsa paket yazilmaz. Ayni kaynaktan ayni paket
# cikar (tarih paketlenen dosyalarin son commit'i; SOURCE_DATE_EPOCH ezer).
import gzip
import hashlib
import io
import os
import py_compile
import re
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIN = ROOT / "TiviAtv-FHD"
DIST = ROOT / "dist"
PKG = "enigma2-plugin-skins-tiviatv-fhd"
E2PY = "usr/lib/enigma2/python"

# paketteki yol: kaynak dosya
LAYOUT = {}
for f in sorted(SKIN.iterdir()):
	if f.is_file():
		LAYOUT["usr/share/enigma2/TiviAtv-FHD/" + f.name] = f
for name in ("LICENSE", "NOTICE"):
	LAYOUT["usr/share/enigma2/TiviAtv-FHD/" + name] = ROOT / name
for f in sorted((SKIN / "converter").glob("*.py")):
	LAYOUT[E2PY + "/Components/Converter/" + f.name] = f
for f in sorted((ROOT / "plugin" / "TiviAtvFont").glob("*.py")):
	LAYOUT[E2PY + "/Plugins/Extensions/TiviAtvFont/" + f.name] = f

# yazi tipi secimi yukseltmede korunsun: opkg degistirilmis conffile'i ezmez
CONFFILES = ["/usr/share/enigma2/TiviAtv-FHD/fonts.xml"]

# fonts.xml conffile: kullanici yazi tipini degistirdiyse opkg onu birakir, yeni
# sablonu fonts.xml-opkg'ye yazar. Yeni sablondaki takma adlar (alias) eksik
# kalmasin diye sablon alinir, kullanicinin dort font satiri (TM/TMM/TMB/TMX ve
# ustundeki aile yorumu) icine konur.
POSTINST = """#!/bin/sh
D="$PKG_ROOT/usr/share/enigma2/TiviAtv-FHD"
if [ -f "$D/fonts.xml-opkg" ]; then
	if [ "$(grep -c 'name="TM[MBX]*"' "$D/fonts.xml")" = 4 ]; then
		awk '
			FNR == 1 { file++ }
			file == 1 { if ($0 ~ /name="TM[MBX]*"/) { if (prev ~ /<!--/) sel[++n] = prev; sel[++n] = $0 } prev = $0; next }
			/name="TM[MBX]*"/ { held = ""; if (!done) { for (i = 1; i <= n; i++) print sel[i]; done = 1 } next }
			{ if (held != "") print held; held = "" }
			/^[ \t]*<!-- .* -->[ \t]*$/ { held = $0; next }
			{ print }
			END { if (held != "") print held }
		' "$D/fonts.xml" "$D/fonts.xml-opkg" > "$D/fonts.xml.yeni" && mv "$D/fonts.xml.yeni" "$D/fonts.xml"
	fi
	rm -f "$D/fonts.xml-opkg" "$D/fonts.xml.yeni"
fi
echo ""
echo "TiviATV FHD installed."
echo "  Skin    : Menu > Setup > Usage & GUI > Skin Settings"
echo "  Typeface: Menu > Setup > Usage & GUI > TiviATV Font"
echo "If the skin is already active, the new version loads when the GUI restarts."
exit 0
"""

# yukseltmede ($1 = upgrade) dokunmaz; kaldirmada geride kalanlari (Python
# onbellegi, fonts.xml-opkg) siler. $PKG_ROOT: opkg'nin cevrimdisi kok dizini.
POSTRM = """#!/bin/sh
case "$1" in
	remove|purge)
		rm -rf "$PKG_ROOT/usr/share/enigma2/TiviAtv-FHD" \\
		       "$PKG_ROOT/usr/lib/enigma2/python/Plugins/Extensions/TiviAtvFont"
		rm -f "$PKG_ROOT"/usr/lib/enigma2/python/Components/Converter/__pycache__/TiviAtvSignal.* \\
		      "$PKG_ROOT"/usr/lib/enigma2/python/Components/Converter/__pycache__/TiviAtvText.* \\
		      "$PKG_ROOT"/usr/lib/enigma2/python/Components/Converter/__pycache__/TiviAtvEcm.*
		echo "TiviATV FHD removed. If it was the active skin, the GUI returns to the default skin when it restarts."
		;;
esac
exit 0
"""


def version():
	ver = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
	if not re.fullmatch(r"\d+\.\d+\.\d+", ver):
		sys.exit("VERSION gecersiz: %r (beklenen 1.2.3)" % ver)
	return ver


def build_time():
	if os.environ.get("SOURCE_DATE_EPOCH"):
		return int(os.environ["SOURCE_DATE_EPOCH"])
	# paketlenen dosyalarin son commit'i: dist/'in kendi commit'i tarihi kaydirmaz
	paths = ["VERSION", "LICENSE", "NOTICE", "TiviAtv-FHD", "plugin", "tools/build_ipk.py"]
	out = subprocess.run(["git", "log", "-1", "--format=%at", "--"] + paths, cwd=ROOT, capture_output=True, text=True)
	return int(out.stdout.strip()) if out.returncode == 0 and out.stdout.strip() else 0


def check():
	"""Paket ancak bunlar gecerse yazilir."""
	lint = subprocess.run([sys.executable, str(ROOT / "tools" / "lint_skin.py")], capture_output=True, text=True)
	if lint.returncode != 0:
		sys.exit("lint_skin.py gecmedi:\n" + lint.stdout[-3000:] + lint.stderr[-2000:])
	with tempfile.TemporaryDirectory() as tmp:
		for dest, src in LAYOUT.items():
			if src.suffix == ".py":
				try:
					py_compile.compile(str(src), cfile=os.path.join(tmp, "x.pyc"), doraise=True)
				except py_compile.PyCompileError as err:
					sys.exit("derlenemedi: %s\n%s" % (src, err))
	# nmsbd.ttf kutunun kendi fontu (/usr/share/fonts), pakette yok
	fonts = ET.parse(SKIN / "fonts.xml").getroot().find("fonts")
	missing = [f.get("filename") for f in fonts.findall("font")
	           if f.get("filename") != "nmsbd.ttf" and not (SKIN / f.get("filename")).exists()]
	if missing:
		sys.exit("fonts.xml'in baktigi dosya yok: %s" % ", ".join(missing))


def tar_gz(members, mtime):
	"""members: [(ad, bayt ya da None = klasor, kip)] -> gzip'li tar, sahip root:root"""
	buf = io.BytesIO()
	with gzip.GzipFile(fileobj=buf, mode="wb", mtime=mtime) as gz:
		with tarfile.open(fileobj=gz, mode="w", format=tarfile.GNU_FORMAT) as tar:
			for name, data, mode in members:
				info = tarfile.TarInfo(name)
				info.uid = info.gid = 0
				info.uname = info.gname = "root"
				info.mtime = mtime
				info.mode = mode
				if data is None:
					info.type = tarfile.DIRTYPE
					tar.addfile(info)
				else:
					info.size = len(data)
					tar.addfile(info, io.BytesIO(data))
	return buf.getvalue()


def ar(members, mtime):
	"""Klasik ar arsivi (opkg ve dpkg'nin bekledigi bicim)."""
	out = [b"!<arch>\n"]
	for name, data in members:
		out.append(b"%-16s%-12d%-6d%-6d%-8s%-10d`\n" % (name.encode(), mtime, 0, 0, b"100644", len(data)))
		out.append(data + (b"\n" if len(data) % 2 else b""))
	return b"".join(out)


def main():
	ver = version()
	check()
	mtime = build_time()

	dirs, files, total = set(), [], 0
	for dest, src in sorted(LAYOUT.items()):
		parts = dest.split("/")
		for i in range(1, len(parts)):
			dirs.add("/".join(parts[:i]))
		data = src.read_bytes()
		total += len(data)
		files.append(("./" + dest, data, 0o644))
	data_tar = tar_gz([("./", None, 0o755)] + [("./%s/" % d, None, 0o755) for d in sorted(dirs)] + files, mtime)

	control = "\n".join([
		"Package: " + PKG,
		"Version: " + ver,
		"Description: TiviATV FHD - TiviMate-style 1920x1080 skin for openATV, without PNGs (Inter typeface)",
		"Section: skins",
		"Priority: optional",
		"Maintainer: Furkan YILDIRIM",
		"Homepage: https://github.com/fyildirim-debug/tiviatv-fhd",
		"Architecture: all",
		"Installed-Size: %d" % max(1, total // 1024),
		"",
	]).encode("utf-8")
	control_tar = tar_gz([
		("./", None, 0o755),
		("./control", control, 0o644),
		("./conffiles", ("\n".join(CONFFILES) + "\n").encode(), 0o644),
		("./postinst", POSTINST.encode(), 0o755),
		("./postrm", POSTRM.encode(), 0o755),
	], mtime)
	ipk = ar([("debian-binary", b"2.0\n"), ("control.tar.gz", control_tar), ("data.tar.gz", data_tar)], mtime)

	DIST.mkdir(exist_ok=True)
	for old in DIST.glob(PKG + "_*"):
		old.unlink()
	out = DIST / ("%s_%s_all.ipk" % (PKG, ver))
	out.write_bytes(ipk)
	sha = hashlib.sha256(ipk).hexdigest()
	# LF: Windows'ta uretilse de kutuda sha256sum -c calissin
	with open(str(out) + ".sha256", "w", newline="\n") as handle:
		handle.write("%s  %s\n" % (sha, out.name))
	print("paket : %s" % out.relative_to(ROOT))
	print("surum : %s | dosya: %d | boyut: %d KB" % (ver, len(files), len(ipk) // 1024))
	print("sha256: %s" % sha)


if __name__ == "__main__":
	main()
