# skin.xml'deki gercek renk ve koordinatlardan preview.png uretir.
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "TiviAtv-FHD"
TARGETS = [SRC, ROOT / "TiviAtv-FHD-PNG"]

W, H = 1920, 1080
S = 0.5                     # 960x540 cikti
root = ET.parse(SRC / "skin.xml").getroot()

colors, grads = {}, {}
for tag in root.findall("colors"):
    for c in tag.findall("color"):
        v = c.get("value", "")
        (grads if "," in v else colors)[c.get("name")] = v


def rgba(v, default=(255, 255, 255, 255)):
    v = colors.get(v, v)
    if not isinstance(v, str) or not v.startswith("#"):
        return default
    h = v[1:]
    if len(h) == 6:
        a, h = 0, h
    elif len(h) == 8:
        a, h = int(h[:2], 16), h[2:]
    else:
        return default
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (r, g, b, 255 - a)


def C(name):
    return rgba(name)


def px(v):
    return int(round(v * S))


img = Image.new("RGB", (px(W), px(H)), C("bg")[:3])
d = ImageDraw.Draw(img, "RGBA")


def font(path, size):
    return ImageFont.truetype(str(SRC / path), px(size))


f_num = font("Barlow-Bold.ttf", 52)
f_ch = font("Barlow-SemiBold.ttf", 44)
f_prov = font("Barlow-Regular.ttf", 24)
f_now = font("Barlow-Regular.ttf", 34)
f_time = font("Barlow-Regular.ttf", 28)
f_clock = font("Barlow-Bold.ttf", 58)
f_rem = font("Barlow-SemiBold.ttf", 26)
f_pill = font("Barlow-SemiBold.ttf", 19)
f_row = font("Barlow-SemiBold.ttf", 32)
f_sub = font("Barlow-Regular.ttf", 22)

# ---- arka plan: yayin goruntusu yerine atmosfer
for y in range(px(H)):
    t = y / px(H)
    d.line([(0, y), (px(W), y)],
           fill=(int(22 + 20 * (1 - t)), int(30 + 24 * (1 - t)), int(44 + 30 * (1 - t))))
d.ellipse([px(-200), px(-160), px(900), px(620)], fill=(48, 66, 94, 120))
d.ellipse([px(1150), px(420), px(2100), px(1100)], fill=(74, 52, 66, 110))

# ---- sol panel + kanal listesi (ChannelSelection duzeni)
d.rectangle([0, 0, px(1060), px(H)], fill=C("panelBg"))
d.line([(px(1058), 0), (px(1058), px(H))], fill=C("line")[:3], width=max(1, px(2)))
d.text((px(48), px(46)), "Favoriler (TV)", font=f_ch, fill=C("text")[:3])

CH = [("101", "TRT 1 HD", "Teskilat"), ("102", "Show TV HD", "Kalp Yarasi"),
      ("103", "ATV HD", "Sadakatsiz"), ("104", "Star TV HD", "Yasak Elma"),
      ("105", "Kanal D HD", "Camdaki Kiz"), ("106", "FOX HD", "Ana Haber"),
      ("107", "TV8 HD", "MasterChef"), ("108", "NOW TV HD", "Kizil Goncalar"),
      ("109", "TRT Spor HD", "Sup Ozet"), ("110", "beIN SPORTS 1", "Derbi")]
top, rowh = 150, 82
for i, (n, nm, ev) in enumerate(CH):
    y = top + i * rowh
    sel = i == 3
    if sel:
        d.rounded_rectangle([px(44), px(y), px(1016), px(y + rowh - 6)],
                            radius=px(14), fill=C("accent")[:3])
    ink = C("onAccent")[:3] if sel else C("text")[:3]
    dim = C("onAccent")[:3] if sel else C("textDim")[:3]
    d.text((px(70), px(y + 14)), n, font=f_sub, fill=dim)
    d.text((px(150), px(y + 8)), nm, font=f_row, fill=ink)
    d.text((px(150), px(y + 46)), ev, font=f_sub, fill=dim)

# ---- sag: canli goruntu kutusu
d.rounded_rectangle([px(1096), px(142), px(1880), px(590)], radius=px(18),
                    fill=C("surface2")[:3])
for y in range(px(150), px(582)):
    t = (y - px(150)) / (px(582) - px(150))
    d.line([(px(1104), y), (px(1872), y)],
           fill=(int(33 - 15 * t), int(50 - 22 * t), int(74 - 40 * t)))

# ---- sag: EPG karti
d.rounded_rectangle([px(1096), px(622), px(1880), px(1018)], radius=px(18),
                    fill=C("surface2")[:3])
d.rounded_rectangle([px(1128), px(650), px(1248), px(684)], radius=px(17),
                    fill=C("accent")[:3])
d.text((px(1152), px(656)), "SIMDI", font=f_pill, fill=C("onAccent")[:3])
d.text((px(1128), px(700)), "Teskilat", font=f_ch, fill=C("text")[:3])
d.text((px(1128), px(742)), "20:00 - 21:45", font=f_time, fill=C("textDim")[:3])
d.rounded_rectangle([px(1128), px(792), px(1848), px(798)], radius=px(3), fill=C("line")[:3])
d.rounded_rectangle([px(1128), px(792), px(1582), px(798)], radius=px(3), fill=C("accent")[:3])
d.rounded_rectangle([px(1128), px(814), px(1264), px(848)], radius=px(17), fill=C("surface3")[:3])
d.text((px(1146), px(820)), "SONRAKI", font=f_pill, fill=C("textDim")[:3])
d.text((px(1128), px(862)), "Ana Haber Bulteni", font=f_now, fill=C("textDim")[:3])

# ---- renk tuslari
for i, (lbl, bgc, fgc) in enumerate([("Tumu", "redSoft", "live"), ("Uydular", "greenSoft", "ok"),
                                     ("Saglayici", "yellowSoft", "warn"),
                                     ("Favoriler", "blueSoft", "accent")]):
    x = 48 + i * 244
    d.rounded_rectangle([px(x), px(1000), px(x + 228), px(1052)], radius=px(26), fill=C(bgc)[:3])
    w = d.textlength(lbl, font=f_pill)
    d.text((px(x + 114) - w / 2, px(1014)), lbl, font=f_pill, fill=C(fgc)[:3])

img.save(TARGETS[0] / "preview.png")
for t in TARGETS[1:]:
    img.save(t / "preview.png")
    img.save(t / "prev.png")
print(f"preview.png uretildi ({img.width}x{img.height}) ->", ", ".join(str(t) for t in TARGETS))
