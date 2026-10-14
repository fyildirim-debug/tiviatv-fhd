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
RAW = "https://raw.githubusercontent.com/openatv/enigma2/master/lib/python/"
UPSTREAM = {
    "skin.py": RAW + "skin.py",
    "ServiceList.py": RAW + "Components/ServiceList.py",
    # kendi applySkin'ini yapan bilesenler (EPG listesi, zaman cetveli, ikon fontu)
    "EpgList.py": RAW + "Components/EpgList.py",
    "Pixmap.py": RAW + "Components/Pixmap.py",
    "ScrollLabel.py": RAW + "Components/ScrollLabel.py",
    "Timers.py": RAW + "Screens/Timers.py",
}
for fname, url in UPSTREAM.items():
    dest = CACHE / fname
    if not dest.exists():
        print(f"indiriliyor: {fname}")
        urllib.request.urlretrieve(url, dest)
SKINPY = CACHE / "skin.py"

errors, warns = [], []

# ---- supported attributes straight out of the engine ----
src = open(SKINPY, encoding="utf-8").read()
supported = set(re.findall(r"^\tdef ([a-zA-Z]+)\(self, value\)", src, re.M))
# applySkin icindeki ic fonksiyon adlari attribute adidir
for fname in ("ServiceList.py", "Timers.py"):
    comp = open(CACHE / fname, encoding="utf-8").read()
    supported |= set(re.findall(r"^\t\tdef ([a-zA-Z]+)\(value\)", comp, re.M))
for fname in ("EpgList.py", "Pixmap.py", "ScrollLabel.py"):
    comp = open(CACHE / fname, encoding="utf-8").read()
    supported |= set(re.findall(r'attrib(?:ute)? == "(\w+)"', comp))
    supported |= set(re.findall(r'attributes(?:\.get\(|\[)"(\w+)"', comp))
    for group in re.findall(r"attribute in \(([^)]*)\)", comp):
        supported |= set(re.findall(r'"(\w+)"', group))
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

# ucuncu parti bilesenlerin kendi applySkin'inde okunan attribute'lar.
# EMC MovieCenter: Cool* sayi / font / boyut (CoolTitleColor gibi adlar da 0/1
# bayragi, renk degil), *Color'lar renk.
EMC_COLORS = {"TitleColor", "DateColor", "DefaultColor", "BackColor", "BackColorSel", "FrontColorSel",
    "UnwatchedColor", "WatchingColor", "FinishedColor", "RecordingColor"}
supported |= EMC_COLORS | {"CoolFont", "CoolSelectFont", "CoolDateFont", "CoolDirPos", "CoolMoviePos",
    "CoolMovieHPos", "CoolMovieSize", "CoolMoviePiconPos", "CoolMoviePiconSize", "CoolIconHPos", "CoolIconPos",
    "CoolIconSize", "CoolFolderSize", "CoolTitleColor", "CoolDatePos", "CoolDateHPos", "CoolDateWidth",
    "CoolDateColor", "CoolHighlightColor", "CoolTimePos", "CoolCSWidth", "CoolCSPos", "CoolDirInfoWidth",
    "CoolSelNumTxtWidth", "CoolProgressPos", "CoolProgressHPos", "CoolBarPos", "CoolBarHPos", "CoolBarSize",
    "CoolBarSizeSa", "CoolPiconPos", "CoolPiconHPos", "CoolPiconWidth", "CoolPiconHeight"}
COLOR_ATTRS |= EMC_COLORS

tree = ET.parse(SKIN)
root = tree.getroot()


# <include filename="..."/> enigma2'de skin klasorune gore cozulur ve ayni
# skin gibi yuklenir (skin.py loadSkin). Font/renk tanimlari oradan da gelir.
def skin_parts(node, base, seen):
    yield node
    for inc in node.findall("include"):
        fname = inc.get("filename", "")
        path = (base / fname).resolve()
        if not fname or path in seen:
            continue
        if not path.exists():
            errors.append(f"<include>: dosya yok -> {fname!r}")
            continue
        seen.add(path)
        yield from skin_parts(ET.parse(path).getroot(), path.parent, seen)


parts = list(skin_parts(root, SKIN.parent, {SKIN.resolve()}))

colors, gradients, fonts = set(), set(), set()
for part in parts:
    for tag in part.findall("colors"):
        for c in tag.findall("color"):
            (gradients if "," in c.get("value", "") else colors).add(c.get("name"))
    for tag in part.findall("fonts"):
        for f in tag.findall("font"):
            fonts.add(f.get("name"))
        for a in tag.findall("alias"):
            fonts.add(a.get("name"))

COLOR_LIST_ATTRS = {"iconColors"}  # her glif icin bir renk, virgullu

# skin.py enigma2icons.ttf'yi kendisi kaydeder (ikon glifleri)
fonts.add("enigma2icons")

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


screens = [s for part in parts for s in part.findall("screen")]
for scr in screens:
    sname = scr.get("name", "?")
    # <templates> / <template> (openATV Listbox sablonu) ogeleri widget attribute'u degil
    skip = {id(t) for tag in ("templates", "template") for tmpl in scr.iter(tag) for t in tmpl.iter()}
    for el in scr.iter():
        if id(el) in skip:
            continue
        where = f"[{sname}] <{el.tag}>"
        if el is scr:
            where = f"[{sname}] <screen>"
        # adi / kaynagi / addon'u olmayan widget'i skin.py SkinError ile atlar
        if el.tag == "widget" and not (el.get("name") or el.get("source") or el.get("addon")):
            errors.append(f"{where}: widget'in name / source / addon'u yok (atlanir)")
        for attr, val in el.attrib.items():
            if el.tag == "convert" or el.tag == "applet":
                continue
            if attr not in supported:
                warns.append(f"{where}: bilinmeyen attribute {attr!r}")
            if attr in COLOR_LIST_ATTRS and val:
                for c in val.split(","):
                    check_color(where, attr, c.strip())
            elif attr in COLOR_ATTRS and val:
                check_color(where, attr, val)
            # eLabel'de borderWidth/borderColor yazinin dis cizgisidir (elabel.h);
            # kutu kenari widgetBorderWidth/widgetBorderColor ile cizilir
            # saydam yazi etiketinde dis cizgi bilerek kullanilir (acik zeminde okunurluk)
            if attr in ("borderWidth", "borderColor") and val not in ("0", "") and \
               (el.tag == "eLabel" or el.get("render") == "Label") and \
               not (el.get("transparent") == "1" and el.get("font")):
                warns.append(f"{where}: {attr} eLabel'de yazi kenaridir, kutu icin widget{attr[0].upper()}{attr[1:]}")
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

# AtileHD_About'taki surum yazisi VERSION ile ayni olmali
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
for scr in screens:
    if scr.get("name") == "AtileHD_About":
        shown = [el.get("text", "") for el in scr.iter("eLabel") if el.get("text", "").startswith("Version ")]
        if shown != ["Version " + VERSION]:
            errors.append(f"[AtileHD_About] surum yazisi {shown} != VERSION {VERSION!r}")

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
