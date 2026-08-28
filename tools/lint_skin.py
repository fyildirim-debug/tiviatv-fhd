import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIN = ROOT / "TiviAtv-FHD" / "skin.xml"
CACHE = ROOT / ".cache"
CACHE.mkdir(exist_ok=True)

# Motorun gercek attribute listesi openATV kaynagindan gelir.
UPSTREAM = {
    "skin.py": "https://raw.githubusercontent.com/openatv/enigma2/master/lib/python/skin.py",
    "ServiceList.py": "https://raw.githubusercontent.com/openatv/enigma2/master/lib/python/Components/ServiceList.py",
}
for fname, url in UPSTREAM.items():
    dest = CACHE / fname
    if not dest.exists():
        print(f"indiriliyor: {fname}")
        urllib.request.urlretrieve(url, dest)
SKINPY = CACHE / "skin.py"
SVCLIST = CACHE / "ServiceList.py"

errors, warns = [], []

# ---- supported attributes straight out of the engine ----
src = open(SKINPY, encoding="utf-8").read()
supported = set(re.findall(r"^\tdef ([a-zA-Z]+)\(self, value\)", src, re.M))
svc = open(SVCLIST, encoding="utf-8").read()
supported |= set(re.findall(r"^\t\tdef ([a-zA-Z]+)\(value\)", svc, re.M))
# component-level attributes handled outside skin.py's AttributeParser
supported |= {
    "name", "source", "render", "position", "size", "text", "pixmap", "pixmaps",
    "EntryBorderColor", "EntryBackgroundColor", "EntryBackgroundColorSelected",
    "hidePip", "id", "value", "filename", "scale", "replacement", "font",
    "entryFont", "valueFont", "headerFont", "entryLeftOffset", "indentSize",
    "headerLeftOffset", "enableWrapAround", "color", "type", "xres", "yres", "bpp",
}

COLOR_ATTRS = {a for a in supported if "olor" in a} | {"itemGradient", "itemGradientSelected",
    "itemGradientMarked", "itemGradientMarkedAndSelected", "backgroundGradient",
    "backgroundGradientSelected", "scrollbarBackgroundGradient", "scrollbarForegroundGradient"}

tree = ET.parse(SKIN)
root = tree.getroot()

colors, gradients, fonts = set(), set(), set()
for tag in root.findall("colors"):
    for c in tag.findall("color"):
        (gradients if "," in c.get("value", "") else colors).add(c.get("name"))
for tag in root.findall("fonts"):
    for f in tag.findall("font"):
        fonts.add(f.get("name"))
    for a in tag.findall("alias"):
        fonts.add(a.get("name"))

HEX = re.compile(r"^#[0-9a-fA-F]{6}$|^#[0-9a-fA-F]{8}$")


def check_color(where, attr, val):
    if "," in val:
        parts = [p.strip() for p in val.split(",")]
        for p in parts[:2]:
            if not HEX.match(p) and p not in colors:
                errors.append(f"{where}: {attr} gradient rengi gecersiz -> {p!r}")
        if parts[-1] not in ("vertical", "horizontal", "0", "1") and \
           parts[-2] not in ("vertical", "horizontal"):
            errors.append(f"{where}: {attr} gradient yonu eksik -> {val!r}")
        return
    if HEX.match(val) or val in colors or val in gradients:
        return
    errors.append(f"{where}: {attr} bilinmeyen renk -> {val!r}")


screens = root.findall("screen")
for scr in screens:
    sname = scr.get("name", "?")
    for el in scr.iter():
        where = f"[{sname}] <{el.tag}>"
        if el is scr:
            where = f"[{sname}] <screen>"
        for attr, val in el.attrib.items():
            if el.tag == "convert" or el.tag == "applet":
                continue
            if attr not in supported:
                warns.append(f"{where}: bilinmeyen attribute {attr!r}")
            if attr in COLOR_ATTRS and val:
                check_color(where, attr, val)
            if attr == "font" and val:
                fam = val.split(";")[0]
                if fam not in fonts:
                    errors.append(f"{where}: tanimsiz font {fam!r}")
            if attr == "cornerRadius" or attr.startswith("itemCornerRadius") or attr == "scrollbarRadius":
                head = val.split(";")[0].strip()
                if not head.isdigit():
                    errors.append(f"{where}: {attr} sayisal degil -> {val!r}")

    # geometry bounds
    ssize = scr.get("size", "")
    if re.match(r"^\d+,\d+$", ssize):
        sw, sh = (int(x) for x in ssize.split(","))
        for el in scr.iter():
            if el is scr:
                continue
            pos, size = el.get("position", ""), el.get("size", "")
            if re.match(r"^-?\d+,-?\d+$", pos) and re.match(r"^\d+,\d+$", size):
                x, y = (int(v) for v in pos.split(","))
                w, h = (int(v) for v in size.split(","))
                if x + w > sw or y + h > sh:
                    errors.append(
                        f"[{sname}] <{el.tag} {el.get('name') or el.get('source') or ''}>: "
                        f"ekran disina tasiyor {x}+{w}x{y}+{h} > {sw}x{sh}")

print(f"XML gecerli. {len(screens)} ekran, {len(colors)} duz renk, {len(gradients)} gradient, {len(fonts)} font.")
print(f"Motorun destekledigi attribute sayisi: {len(supported)}")
print()
if errors:
    print(f"--- HATA ({len(errors)}) ---")
    for e in errors:
        print(" X", e)
else:
    print("--- HATA YOK ---")
print()
if warns:
    print(f"--- UYARI ({len(warns)}) ---")
    for w in sorted(set(warns)):
        print(" !", w)
else:
    print("--- UYARI YOK ---")
sys.exit(1 if errors else 0)
