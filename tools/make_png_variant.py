# TiviAtv-FHD (sifir PNG, openATV 7.3+)  ->  TiviAtv-FHD-PNG (her surumde ayni gorunur)
#
# skin.xml'deki cornerRadius + backgroundColor tasiyan her elemani okur, TAM O
# BOYUTTA yuvarlak kose + gradient tasiyan bir PNG uretir ve elemanin arkasina
# bir <ePixmap alphatest="blend"> koyar. Boylece motorun cizim ozelliklerine hic
# ihtiyac kalmaz:
#   - openATV 7.0-7.2 (cornerRadius yok)        -> dogru gorunur
#   - OpenSkin Designer (cornerRadius bilmiyor) -> dogru gorunur
#
# PNG'ler elemanin tam olcusunde uretildigi icin hicbir yerde esnetme yok.
# Alfa korunur: enigma2'nin #AARRGGBB (AA = seffaflik) degeri PNG alfasina
# cevrilir, alphatest="blend" ile tam alfa harmanlamasi yapilir.
import hashlib
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "TiviAtv-FHD"
DST = ROOT / "TiviAtv-FHD-PNG"
PNGDIR = DST / "png"

if DST.exists():
    shutil.rmtree(DST)
PNGDIR.mkdir(parents=True)

tree = ET.parse(SRC / "skin.xml")
root = tree.getroot()

colors, gradients = {}, {}
for tag in root.findall("colors"):
    for c in tag.findall("color"):
        v = c.get("value", "")
        (gradients if "," in v else colors)[c.get("name")] = v

HEX = re.compile(r"^#[0-9a-fA-F]{6}$|^#[0-9a-fA-F]{8}$")


def rgba(v):
    """enigma2 #AARRGGBB (AA = seffaflik) -> (r,g,b,a)"""
    v = colors.get(v, v)
    if not isinstance(v, str) or not v.startswith("#"):
        return None
    h = v[1:]
    if len(h) == 6:
        a, h = 0, h
    elif len(h) == 8:
        a, h = int(h[:2], 16), h[2:]
    else:
        return None
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255 - a)


def fill_spec(value):
    """-> ('solid', c) | ('grad', c1, c2, 'v'|'h')  ya da None"""
    if not value:
        return None
    v = gradients.get(value, value)
    if "," in v:
        bits = [b.strip() for b in v.split(",")]
        stops = [b for b in bits if HEX.match(b) or b in colors]
        direction = "h" if "horizontal" in bits else "v"
        c1 = rgba(stops[0])
        c2 = rgba(stops[-1]) if len(stops) > 1 else c1
        if c1 is None or c2 is None:
            return None
        return ("grad", c1, c2, direction)
    c = rgba(v)
    return ("solid", c) if c else None


EDGE = {"topLeft": (1, 0, 0, 0), "topRight": (0, 1, 0, 0),
        "bottomRight": (0, 0, 1, 0), "bottomLeft": (0, 0, 0, 1),
        "top": (1, 1, 0, 0), "bottom": (0, 0, 1, 1),
        "left": (1, 0, 0, 1), "right": (0, 1, 1, 0)}


def parse_radius(value):
    bits = [b.strip() for b in value.split(";")]
    r = int(bits[0])
    if len(bits) == 1:
        return r, (True, True, True, True)
    mask = [0, 0, 0, 0]
    for e in bits[1].split(","):
        for i, v in enumerate(EDGE.get(e.strip(), (0, 0, 0, 0))):
            mask[i] |= v
    return r, tuple(bool(m) for m in mask)


made = {}


def make_png(w, h, radius_attr, fill, tag="bg"):
    r, corners = parse_radius(radius_attr) if radius_attr else (0, (True,) * 4)
    r = max(0, min(r, w // 2, h // 2))
    key = hashlib.md5(f"{w}x{h}|{radius_attr}|{fill}".encode()).hexdigest()[:10]
    if key in made:
        return made[key]
    fname = f"{tag}_{w}x{h}_r{r}_{key}.png"

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if fill[0] == "solid":
        body = Image.new("RGBA", (w, h), fill[1])
    else:
        _, c1, c2, d = fill
        body = Image.new("RGBA", (w, h))
        px = body.load()
        n = h if d == "v" else w
        for i in range(n):
            t = i / max(1, n - 1)
            col = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(4))
            if d == "v":
                for x in range(w):
                    px[x, i] = col
            else:
                for y in range(h):
                    px[i, y] = col

    # Kose maskesi: ImageDraw kenar yumusatma yapmaz, o yuzden SS katiyla
    # buyuk cizip LANCZOS ile kucultuyoruz -> yumusak, basamaksiz kose.
    SS = 4
    big = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(big).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1],
                                          radius=r * SS, fill=255, corners=corners)
    mask = big.resize((w, h), Image.LANCZOS)

    # Alfayi koru: govdenin kendi alfasi ile kose maskesini CARP.
    # (paste degil carpma; boylece yari saydam bir dolgu maskeden gecerken
    #  saydamligini kaybetmez.)
    body.putalpha(ImageChops.multiply(body.getchannel("A"), mask))
    img.alpha_composite(body)
    img.save(PNGDIR / fname)
    made[key] = f"png/{fname}"
    return made[key]


def size_of(el):
    s = (el.get("size") or "").split(",")
    if len(s) != 2:
        return None
    try:
        return int(s[0]), int(s[1])
    except ValueError:
        return None


stats = {"pixmap": 0, "progress": 0, "selection": 0, "skipped": 0}

for screen in root.findall("screen"):
    out = []
    for el in list(screen):
        cr = el.get("cornerRadius")
        bg = el.get("backgroundColor")
        transparent = el.get("transparent") == "1"
        dims = size_of(el)
        render = el.get("render", "")

        # ilerleme cubugu / kaydirici: dolgu pixmap'i
        is_bar = render == "Progress" or el.get("name") in ("Volume", "Mute", "slider")
        if is_bar and dims:
            fg = fill_spec(el.get("foregroundColor"))
            if fg:
                p = make_png(dims[0], dims[1], cr or "0", fg, "fill")
                el.set("pixmap", p)
                el.attrib.pop("foregroundColor", None)
                el.attrib.pop("cornerRadius", None)
                stats["progress"] += 1
            out.append(el)
            continue

        # listbox secim vurgusu
        if el.get("itemGradientSelected") or el.get("itemCornerRadiusSelected"):
            sel = fill_spec(el.get("itemGradientSelected"))
            rad = el.get("itemCornerRadiusSelected", "0")
            if sel and dims:
                ih = el.get("itemHeight") or el.get("serviceItemHeight")
                rowh = int(ih) if ih else max(40, dims[1] // 10)
                el.set("selectionPixmap", make_png(dims[0], rowh, rad, sel, "sel"))
                stats["selection"] += 1
            for a in ("itemGradientSelected", "itemCornerRadiusSelected", "itemCornerRadius"):
                el.attrib.pop(a, None)

        # yuvarlak koseli dolu kutu -> arkasina ePixmap
        if cr and bg and not transparent and dims:
            fill = fill_spec(bg)
            if fill:
                pix = ET.Element("ePixmap")
                pix.set("pixmap", make_png(dims[0], dims[1], cr, fill, "bg"))
                pix.set("position", el.get("position", "0,0"))
                pix.set("size", el.get("size"))
                pix.set("alphatest", "blend")
                if el.get("zPosition"):
                    pix.set("zPosition", el.get("zPosition"))
                out.append(pix)
                stats["pixmap"] += 1

                el.attrib.pop("cornerRadius", None)
                if not (el.get("text") or el.tag == "widget" or el.get("name")):
                    continue          # salt dekor -> eLabel'a gerek yok
                el.attrib.pop("backgroundColor", None)
                el.set("transparent", "1")
        elif cr:
            el.attrib.pop("cornerRadius", None)
            stats["skipped"] += 1

        out.append(el)
    screen[:] = out

# gradient kalan yerleri duz renge indir (ornek: fadeUp bandi)
for tag in root.findall("colors"):
    for c in tag.findall("color"):
        v = c.get("value", "")
        if "," in v:
            f = fill_spec(v)
            if f and f[0] == "grad":
                avg = tuple((f[1][k] + f[2][k]) // 2 for k in range(4))
                c.set("value", "#%02x%02x%02x%02x" % (255 - avg[3], avg[0], avg[1], avg[2]))

ET.indent(tree, space="\t")
tree.write(DST / "skin.xml", encoding="utf-8", xml_declaration=False)

for f in list(SRC.glob("Barlow-*.ttf")) + [SRC / "OFL-Barlow.txt", SRC / "preview.png"]:
    if f.exists():
        shutil.copy2(f, DST / f.name)

total_kb = sum(p.stat().st_size for p in PNGDIR.glob("*.png")) / 1024
print(f"yazildi: {DST}")
print(f"  arka plan pixmap : {stats['pixmap']}")
print(f"  ilerleme dolgusu : {stats['progress']}")
print(f"  secim vurgusu    : {stats['selection']}")
print(f"  benzersiz PNG    : {len(made)}  ({total_kb:.0f} KB)")
print(f"  radius'u dusen   : {stats['skipped']}")
