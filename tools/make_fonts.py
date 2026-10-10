# Skin klasorundeki Inter ve Geist statik agirliklarini uretir.
# Google Fonts deposundaki degisken fonttan fontTools ile dort agirlik
# (Regular/Medium/SemiBold/Bold) cikarir; dosya adlari TiviAtvFont eklentisinin
# "Aile-Agirlik.ttf" beklentisine uyar. enigma2 degisken fontta agirlik
# secemez, bu yuzden statik dosya gerekir.
#
#   pip install fonttools
#   python3 tools/make_fonts.py
import urllib.request
from io import BytesIO
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parents[1]
DST = ROOT / "TiviAtv-FHD"
RAW = "https://raw.githubusercontent.com/google/fonts/main/ofl/"

# aile: (degisken font, sabitlenen eksenler)
# Inter opsz 22: metin kesiminin (14) rahat araligi ile baslik kesiminin (32)
# sikiligi arasi; TV'de 22-72 px yazilar icin
FAMILIES = {
	"Inter": ("inter/Inter%5Bopsz%2Cwght%5D.ttf", {"opsz": 22}),
	"Geist": ("geist/Geist%5Bwght%5D.ttf", {}),
}
WEIGHTS = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold"}


def rename(font, family, weight, wght):
	"""Ad tablosunu statik aileye gore yazar (STAT'ta opsz 22 degeri yok)."""
	names = font["name"]
	for nameID in (1, 2, 3, 4, 6, 16, 17, 25):
		names.removeNames(nameID=nameID)
	ribbi = weight in ("Regular", "Bold")
	full = family if weight == "Regular" else "%s %s" % (family, weight)
	names.setName(family if ribbi else full, 1, 3, 1, 0x409)
	names.setName(weight if ribbi else "Regular", 2, 3, 1, 0x409)
	names.setName("%s-%s;TiviATV static" % (family, weight), 3, 3, 1, 0x409)
	names.setName(full, 4, 3, 1, 0x409)
	names.setName("%s-%s" % (family, weight), 6, 3, 1, 0x409)
	if not ribbi:
		names.setName(family, 16, 3, 1, 0x409)
		names.setName(weight, 17, 3, 1, 0x409)
	font["OS/2"].usWeightClass = wght
	selection = font["OS/2"].fsSelection & ~0b1100001  # italik, kalin, normal bitleri
	font["OS/2"].fsSelection = selection | {"Bold": 0x20, "Regular": 0x40}.get(weight, 0)
	font["head"].macStyle = 1 if weight == "Bold" else 0
	if "STAT" in font:
		del font["STAT"]


for family, (src, axes) in FAMILIES.items():
	print("indiriliyor: %s" % family)
	data = urllib.request.urlopen(RAW + src).read()
	license_ = urllib.request.urlopen(RAW + src.split("/")[0] + "/OFL.txt").read()
	(DST / ("OFL-%s.txt" % family)).write_bytes(license_)
	for wght, weight in WEIGHTS.items():
		font = instancer.instantiateVariableFont(TTFont(BytesIO(data)), dict(wght=wght, **axes))
		rename(font, family, weight, wght)
		font.recalcTimestamp = False  # tarih kaynaktan: ayni girdi, ayni dosya
		out = DST / ("%s-%s.ttf" % (family, weight))
		font.save(out)
		print("  %s" % out.name)
