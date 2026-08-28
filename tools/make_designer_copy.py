# Bir skin klasorunu OpenSkin Designer uyumlu hale getirip kopyalar.
#
#   python tools/make_designer_copy.py          -> TiviAtv-FHD      (sifir PNG surumu)
#   python tools/make_designer_copy.py --png    -> TiviAtv-FHD-PNG  (PNG surumu)
#
# Designer (2014) su uc seyi sindiremiyor, kopyada temizleniyor:
#   1. <alias>  - cDataBase.initFonts, <fonts> altindaki HER cocuk dugumden
#                 "filename" okuyor (IL'de dugum adi filtresi yok). <alias>'ta
#                 o attribute yok -> NullReferenceException.
#   2. Blok ici XML yorumlari - yorum dugumunde hic attribute yok, ayni cokme.
#   3. Gradient renk degerleri - "#a,#b,vertical" renk olarak ayristirilamaz.
# Ayrica <windowstyle> icindeki listbox/label/configList/scrolllabel etiketleri
# paketle gelen calisan ornek skinlerde hic yok; guvenlik icin dusuruluyor.
import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ap = argparse.ArgumentParser()
ap.add_argument("--png", action="store_true", help="PNG tabanli varyanti kopyala")
DEFAULT_DESIGNER = next(
    (c for c in (Path.home() / "OneDrive" / "Desktop" / "OpenSkin-Designer-master",
                 Path.home() / "Desktop" / "OpenSkin-Designer-master") if c.is_dir()),
    Path.home() / "Desktop" / "OpenSkin-Designer-master")
ap.add_argument("--designer", default=str(DEFAULT_DESIGNER),
                help="OpenSkin Designer kok klasoru")
args = ap.parse_args()

NAME = "TiviAtv-FHD-PNG" if args.png else "TiviAtv-FHD"
SRC = ROOT / NAME
DST = Path(args.designer) / "skins" / NAME

DST.mkdir(parents=True, exist_ok=True)
s = (SRC / "skin.xml").read_text(encoding="utf-8")

HEX = re.compile(r"^#[0-9a-fA-F]{6}$|^#[0-9a-fA-F]{8}$")
colors = dict(re.findall(r'<color name="([^"]+)"\s+value="(#[0-9a-fA-F]{6,8})"', s))


def parts_of(h):
    h = h[1:]
    if len(h) == 6:
        h = "00" + h
    return [int(h[i:i + 2], 16) for i in (0, 2, 4, 6)]


def flatten(value):
    """'#a,#b,vertical[,1]' -> iki durak renginin ortalamasi olan tek renk."""
    stops = [colors.get(b.strip(), b.strip()) for b in value.split(",")]
    stops = [b for b in stops if HEX.match(b)]
    if not stops:
        return None
    if len(stops) == 1:
        return stops[0]
    a, b = parts_of(stops[0]), parts_of(stops[-1])
    return "#" + "".join(f"{(x + y) // 2:02x}" for x, y in zip(a, b))


def fix_color_tag(m):
    name, val = m.group(1), m.group(2)
    if "," in val:
        new = flatten(val)
        if new:
            return f'<color name="{name}" value="{new}" />'
    return m.group(0)


s = re.sub(r'<color name="([^"]+)"\s+value="([^"]+)"\s*/>', fix_color_tag, s)
s, n_attr = re.subn(r'\b(\w*[Cc]olor\w*|itemGradient\w*)="(#[^"]*,[^"]*)"',
                    lambda m: f'{m.group(1)}="{flatten(m.group(2)) or "#000000"}"', s)

# skin klasorundeki fontlar -> designer'in kendi skins/ klasorune esledigi mutlak yol
s = re.sub(r'filename="(Barlow-[^"]+\.ttf)"',
           lambda m: f'filename="/usr/share/enigma2/{NAME}/{m.group(1)}"', s)

n_alias = len(re.findall(r'<alias\b', s))
s = re.sub(r'^[ \t]*<alias\b[^>]*/>[ \t]*\r?\n', "", s, flags=re.M)


def strip_ws(m):
    inner = re.sub(r'^[ \t]*<(listbox|label|configList|scrolllabel)\b[^>]*/>[ \t]*\r?\n',
                   "", m.group(2), flags=re.M | re.S)
    return m.group(1) + inner + m.group(3)


s, _ = re.subn(r'(<windowstyle\b[^>]*>)(.*?)(</windowstyle>)', strip_ws, s, flags=re.S)

n_comment = len(re.findall(r'<!--.*?-->', s, re.S))
s = re.sub(r'[ \t]*<!--.*?-->[ \t]*\r?\n?', "", s, flags=re.S)
s = re.sub(r'\n{3,}', "\n\n", s)
s = s.replace("<skin>\n", (
    "<skin>\n"
    "\t<!-- BU DOSYA OTOMATIK URETILDI - ELLE DUZENLEME. -->\n"
    f"\t<!-- Kaynak: {NAME}/skin.xml -->\n"), 1)

(DST / "skin.xml").write_text(s, encoding="utf-8")

for f in SRC.glob("Barlow-*.ttf"):
    shutil.copy2(f, DST / f.name)
for extra in ("OFL-Barlow.txt", "preview.png"):
    if (SRC / extra).exists():
        shutil.copy2(SRC / extra, DST / extra)
        if extra == "preview.png":
            shutil.copy2(SRC / extra, DST / "prev.png")

n_png = 0
if (SRC / "png").is_dir():
    if (DST / "png").exists():
        shutil.rmtree(DST / "png")
    shutil.copytree(SRC / "png", DST / "png")
    n_png = len(list((DST / "png").glob("*.png")))

print(f"yazildi: {DST}")
print(f"  kaldirilan <alias> : {n_alias}")
print(f"  kaldirilan yorum   : {n_comment}")
print(f"  duzlestirilen grad.: {n_attr}")
print(f"  kopyalanan PNG     : {n_png}")
