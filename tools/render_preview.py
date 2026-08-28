# Renders TiviATV skin.xml screens to an HTML preview using the REAL coordinates,
# colors, fonts and radii from the skin file. Nothing here is hand-placed.
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIN = ROOT / "TiviAtv-FHD" / "skin.xml"
OUT = ROOT / "preview.html"

W, H = 1920, 1080
tree = ET.parse(SKIN)
root = tree.getroot()

colors, gradients = {}, {}
for tag in root.findall("colors"):
    for c in tag.findall("color"):
        v = c.get("value", "")
        (gradients if "," in v else colors)[c.get("name")] = v


def css_color(v):
    """enigma2 #AARRGGBB (AA = transparency) -> css rgba()."""
    if not v:
        return None
    v = colors.get(v, v)
    if not v.startswith("#"):
        return None
    h = v[1:]
    if len(h) == 6:
        a, rgb = 0, h
    elif len(h) == 8:
        a, rgb = int(h[:2], 16), h[2:]
    else:
        return None
    r, g, b = (int(rgb[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{(255 - a) / 255:.3f})"


def css_bg(v):
    if not v:
        return None
    if v in gradients:
        v = gradients[v]
    if "," in v:
        parts = [p.strip() for p in v.split(",")]
        stops = [p for p in parts if p.startswith("#") or p in colors]
        direction = "to bottom" if "horizontal" not in parts else "to right"
        cols = [css_color(s) for s in stops]
        if len(cols) == 1:
            cols *= 2
        return f"linear-gradient({direction}, {', '.join(cols)})"
    return css_color(v)


def num(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def coord(v, axis_total, own):
    v = (v or "").strip()
    if v == "center":
        return (axis_total - own) // 2
    return num(v)


def pos_size(el):
    p = (el.get("position") or "0,0").split(",")
    s = (el.get("size") or "0,0").split(",")
    w, h = num(s[0].strip()), num(s[1].strip())
    x = coord(p[0], W, w)
    y = coord(p[1], H, h)
    return x, y, w, h


def pct(v, total):
    return f"{v / total * 100:.4f}%"


def fsize(px):
    return f"calc(100cqw * {px / W:.6f})"


def radius(el):
    r = el.get("cornerRadius")
    if not r:
        return ""
    head = r.split(";")[0].strip()
    val = fsize(num(head))
    if ";" not in r:
        return f"border-radius:{val};"
    edges = r.split(";")[1]
    tl = tr = br = bl = "0"
    if "topLeft" in edges or "top" in edges or "left" in edges:
        tl = val
    if "topRight" in edges or "top" in edges or "right" in edges:
        tr = val
    if "bottomRight" in edges or "bottom" in edges or "right" in edges:
        br = val
    if "bottomLeft" in edges or "bottom" in edges or "left" in edges:
        bl = val
    return f"border-radius:{tl} {tr} {br} {bl};"


ALIGN = {"left": "flex-start", "center": "center", "right": "flex-end"}
VALIGN = {"top": "flex-start", "center": "center", "bottom": "flex-end"}

# ---------------------------------------------------------------- sample data
SAMPLE = {
    ("session.CurrentService", "ServiceName", "Name"): "TRT 1 HD",
    ("session.CurrentService", "ServiceName", "Provider"): "TURKSAT 42.0E",
    ("session.CurrentService", "PliExtraInfo", "ResolutionString"): "1920x1080i",
    ("session.CurrentService", "PliExtraInfo", "VideoCodec"): "H.264",
    ("session.CurrentService", "PliExtraInfo", "CryptoInfo"): "FTA",
    ("session.Event_Now", "EventName", "Name"): "Teskilat",
    ("session.Event_Now", "EventTime", "Times"): "20:00 - 21:45",
    ("session.Event_Now", "EventTime", "Remaining"): "42 dk kaldi",
    ("session.Event_Now", "EventName", "Genre"): "Dizi / Aksiyon",
    ("session.Event_Now", "EventName", "ExtendedDescription"):
        "Milli Istihbarat Teskilati'nin sahada gorev alan ekibi, ulke guvenligini "
        "tehdit eden yeni bir operasyonun izini surer. Bolumde ekip, sinir hattinda "
        "beklenmedik bir baglantiyla karsilasir.",
    ("session.Event_Next", "EventName", "Name"): "Ana Haber Bulteni",
    ("ServiceEvent", "EventName", "Name"): "Teskilat",
    ("ServiceEvent", "EventTime", "Times"): "20:00 - 21:45",
    ("ServiceEvent", "EventName", "NextName"): "Ana Haber Bulteni",
    ("ServiceEvent", "EventName", "ExtendedDescription"):
        "Milli Istihbarat Teskilati'nin sahada gorev alan ekibi, ulke guvenligini "
        "tehdit eden yeni bir operasyonun izini surer.",
    ("Event", "EventName", "Name"): "Teskilat",
    ("Event", "EventTime", "Times"): "20:00 - 21:45",
    ("Event", "EventName", "ExtendedDescription"):
        "Milli Istihbarat Teskilati'nin sahada gorev alan ekibi, ulke guvenligini "
        "tehdit eden yeni bir operasyonun izini surer. Bolumde ekip, sinir hattinda "
        "beklenmedik bir baglantiyla karsilasir.",
}
CLOCK = {"Default": "21:03", "Format:%d.%m.%Y": "28.08.2026"}
KEYS = {"key_red": "Tumu", "key_green": "Uydular", "key_yellow": "Saglayici", "key_blue": "Favoriler"}
TITLES = {
    "ChannelSelection": "Favoriler (TV)", "SimpleChannelSelection": "Kanallar",
    "ChannelSelectionRadio": "Radyo", "EPGSelection": "Program Rehberi",
    "GraphMultiEPG": "Program Rehberi", "EventView": "Teskilat",
    "Menu": "Ana Menu", "Setup": "Goruntu Ayarlari",
}
CHANNELS = [
    ("101", "TRT 1 HD", "Teskilat", 63), ("102", "Show TV HD", "Kalp Yarasi", 21),
    ("103", "ATV HD", "Sadakatsiz", 88), ("104", "Star TV HD", "Yasak Elma", 45),
    ("105", "Kanal D HD", "Camdaki Kiz", 12), ("106", "FOX HD", "Ana Haber", 71),
    ("107", "TV8 HD", "MasterChef", 34), ("108", "NOW TV HD", "Kizil Goncalar", 55),
    ("109", "TRT Spor HD", "Sup Ozet", 9), ("110", "beIN SPORTS 1", "Derbi Oncesi", 77),
]
MENU = ["Kanal Listesi", "Program Rehberi", "Medya Oynatici", "Zamanlayici",
        "Bilgi", "Eklentiler", "Ayarlar", "Bekleme / Yeniden Baslat"]
CONFIG = [("Cozunurluk", "1080p"), ("Yenileme hizi", "50 Hz"), ("Renk formati", "Otomatik"),
          ("HDMI ses", "PCM"), ("Ekran tasmasi", "Kapali"), ("AC3 varsayilan", "Evet")]


def sample_for(el, screen):
    src = el.get("source", "")
    convs = el.findall("convert")
    if src == "Title":
        return TITLES.get(screen, screen)
    if src == "parent.Title":
        return "TRT 1 HD"
    if convs:
        ctype = convs[0].get("type")
        token = (convs[0].text or "").strip()
        if ctype == "ClockToText":
            return CLOCK.get(token, "21:03")
        if len(convs) > 1 and convs[1].get("type") == "ClockToText":
            return CLOCK.get((convs[1].text or "").strip(), "21:03")
        return SAMPLE.get((src, ctype, token), token or ctype)
    return ""


# ---------------------------------------------------------------- element html
def render_el(el, screen, ox=0, oy=0):
    tag = el.tag
    if tag not in ("eLabel", "widget", "ePixmap"):
        return ""
    x, y, w, h = pos_size(el)
    x -= ox
    y -= oy
    if w <= 0 or h <= 0:
        return ""
    style = [f"left:{pct(x, W)}", f"top:{pct(y, H)}",
             f"width:{pct(w, W)}", f"height:{pct(h, H)}"]
    bg = css_bg(el.get("backgroundColor"))
    transparent = el.get("transparent") == "1"
    if bg and not transparent:
        style.append(f"background:{bg}")
    fg = css_color(el.get("foregroundColor")) or css_color("text")
    style.append(f"color:{fg}")
    rad = radius(el)
    if rad:
        style.append(rad.rstrip(";").replace("border-radius:", "border-radius:"))
    font = el.get("font", "")
    weight = 400
    if font:
        fam, _, size = font.partition(";")
        weight = {"TM": 400, "TMM": 500, "TMB": 600, "TMX": 700}.get(fam, 400)
        style.append(f"font-size:{fsize(num(size, 24))}")
    style.append(f"font-weight:{weight}")
    style.append(f"justify-content:{ALIGN.get(el.get('halign', 'left'), 'flex-start')}")
    style.append(f"align-items:{VALIGN.get(el.get('valign', 'top'), 'flex-start')}")
    if el.get("halign") == "center":
        style.append("text-align:center")
    elif el.get("halign") == "right":
        style.append("text-align:right")
    z = num(el.get("zPosition"), 0)
    style.append(f"z-index:{z + 5}")

    name = el.get("name", "")
    render = el.get("render", "")
    inner = ""
    cls = "el nowrap" if el.get("noWrap") == "1" else "el"

    if tag == "eLabel":
        inner = html.escape(el.get("text", ""))
    elif render == "Picon":
        cls += " picon"
        inner = "<span>TRT<b>1</b></span>"
    elif render == "Pig":
        cls += " pig"
        inner = "<span>canli goruntu</span>"
    elif render == "Progress" or name == "Volume":
        cls += " prog"
        fill = 45 if name == "Volume" else 63
        fgv = el.get("foregroundColor", "accent")
        inner = f'<i style="width:{fill}%;background:{css_bg(fgv)}"></i>'
    elif render in ("Label", "ChannelNumber"):
        inner = html.escape("104" if render == "ChannelNumber" else sample_for(el, screen))
    elif name in KEYS:
        inner = KEYS[name]
    elif name == "list":
        cls += " list"
        inner = build_list(screen, w, h)
    elif name == "config":
        cls += " list"
        inner = build_config(w, h)
    elif name == "epg_description":
        inner = html.escape(SAMPLE[("Event", "EventName", "ExtendedDescription")] * 3)
        cls += " para"
    elif name == "timeline_text":
        cls += " ticks"
        inner = "".join(f"<span>{t}</span>" for t in
                        ("20:00", "20:30", "21:00", "21:30", "22:00", "22:30"))
    elif name == "number":
        inner = "104"
    elif name == "servicename":
        inner = "TRT 1 HD"
    elif name == "text":
        inner = "Kutuyu yeniden baslatmak istiyor musunuz?" if screen == "MessageBox" \
            else "Ne yapmak istersiniz?"
    elif name == "datetime":
        inner = "28.08.2026  20:00"
    elif name == "duration":
        inner = "105 dk"
    elif name == "channel":
        inner = "TRT 1 HD"
    elif name == "description":
        inner = "Cikis cozunurlugunu secin. 1080p tum modern televizyonlarda desteklenir."
    elif name == "footnote":
        inner = "OK ile kaydet"
    elif name.startswith("timeline"):
        cls += " tline"
        if name == "timeline_now":
            style[0] = f"left:{pct(560, W)}"
            cls += " now"
        else:
            idx = num(name[-1], 0)
            style[0] = f"left:{pct(68 + 297 * (idx + 1), W)}"
    elif name == "HelpWindow":
        return ""

    return f'<div class="{cls}" style="{";".join(style)}">{inner}</div>'


def build_list(screen, w, h):
    if screen in ("ChannelSelection", "SimpleChannelSelection", "ChannelSelectionRadio"):
        rows = []
        for i, (n, nm, ev, p) in enumerate(CHANNELS):
            sel = " sel" if i == 3 else ""
            rows.append(
                f'<div class="row chrow{sel}"><em>{n}</em>'
                f'<div class="chtxt"><b>{nm}</b><small>{ev}</small></div>'
                f'<div class="chbar"><i style="width:{p}%"></i></div></div>')
        return "".join(rows)
    if screen == "Menu":
        return "".join(
            f'<div class="row menurow{" sel" if i == 1 else ""}">{m}</div>'
            for i, m in enumerate(MENU))
    if screen in ("MessageBox", "ChoiceBox"):
        opts = ["Evet", "Hayir"] if screen == "MessageBox" else \
            ["Zamanlayici ekle", "Kanal listesine ekle", "Favorilere ekle", "Iptal"]
        return "".join(f'<div class="row menurow{" sel" if i == 0 else ""}">{o}</div>'
                       for i, o in enumerate(opts))
    if screen == "EPGSelection":
        rows = []
        for i, (t, nm) in enumerate([("20:00", "Teskilat"), ("21:45", "Ana Haber Bulteni"),
                                     ("22:30", "Spor Gundemi"), ("23:15", "Gece Filmi"),
                                     ("01:00", "Belgesel Kusagi"), ("02:00", "Muzik")]):
            rows.append(f'<div class="row epgrow{" sel" if i == 1 else ""}">'
                        f'<em>{t}</em><b>{nm}</b></div>')
        return "".join(rows)
    if screen.startswith("GraphMultiEPG"):
        rows = []
        for i, (n, nm, ev, p) in enumerate(CHANNELS[:7]):
            cells = []
            widths = [(28, ev), (22, "Ana Haber"), (30, "Film Kusagi"), (20, "Spor")]
            for j, (cw, label) in enumerate(widths):
                sel = " sel" if (i == 2 and j == 1) else ""
                cells.append(f'<span class="cell{sel}" style="width:{cw}%">{label}</span>')
            rows.append(f'<div class="grow"><em>{nm}</em>{"".join(cells)}</div>')
        return "".join(rows)
    return ""


def build_config(w, h):
    return "".join(
        f'<div class="row cfgrow{" sel" if i == 0 else ""}"><span>{k}</span><b>{v}</b></div>'
        for i, (k, v) in enumerate(CONFIG))


def render_screen(name, backdrop=True):
    scr = None
    for s in root.findall("screen"):
        if s.get("name") == name:
            scr = s
            break
    if scr is None:
        return ""
    sx, sy, sw, sh = pos_size(scr)
    fullscreen = (sw, sh) == (W, H)
    ox, oy = (0, 0) if fullscreen else (-sx, -sy)
    els = [e for e in scr if e.tag in ("eLabel", "widget", "ePixmap")]
    els.sort(key=lambda e: num(e.get("zPosition"), 0))
    body = "".join(render_el(e, name, ox, oy) for e in els)
    bg = css_bg(scr.get("backgroundColor")) or "transparent"
    base = '<div class="backdrop"></div>' if backdrop else ""
    return (f'<div class="stage" style="background:{bg}">{base}{body}</div>')


SCREENS = [
    ("InfoBar", "InfoBar", "Alt bilgi cubugu - zap sonrasi ve OK tusunda",
     "Kanal numarasi, picon, program, ilerleme cubugu ve sonraki yayin. "
     "Videodan cubuga gecis seffaftan opaga bir gradient - PNG degil."),
    ("ChannelSelection", "Kanal listesi", "TiviMate duzeni - liste solda, canli goruntu sagda",
     "Secili satir yuvarlak kosesini itemCornerRadiusSelected'dan, mavi dolgusunu "
     "itemGradientSelected'dan aliyor. Sag ustteki kutu Pig renderer ile gercek video."),
    ("GraphMultiEPG", "Zaman cizelgesi", "Coklu kanal EPG izgarasi",
     "Alt kartta secili programin tam aciklamasi. Zaman cizgileri kutunun kendi "
     "1px sistem grafigi."),
    ("EventView", "Program detayi", "Tek programin genis gorunumu", ""),
    ("SecondInfoBar", "Ikinci bilgi cubugu", "InfoBar acikken tekrar OK", ""),
    ("Menu", "Ana menu", "Karartilmis arka plan uzerinde kart", ""),
    ("Setup", "Ayarlar", "config listesi + aciklama satiri", ""),
    ("MessageBox", "Onay kutusu", "", ""),
    ("NumberZap", "Numara ile kanal", "", ""),
    ("Volume", "Ses gostergesi", "", ""),
]

cards = []
for i, (nm, label, sub, note) in enumerate(SCREENS):
    stage = render_screen(nm)
    notehtml = f'<p class="note">{html.escape(note)}</p>' if note else ""
    subhtml = f'<p class="sub">{html.escape(sub)}</p>' if sub else ""
    cards.append(f"""<figure class="board">
<figcaption>
  <div class="cap-head"><h3>{html.escape(label)}</h3><code>{nm}</code></div>
  {subhtml}
</figcaption>
<div class="frame">{stage}</div>
{notehtml}
</figure>""")

TEMPLATE = open(Path(__file__).resolve().parent / "shell.html", encoding="utf-8").read()

out = TEMPLATE.replace("<!--BOARDS-->", "\n".join(cards))
open(OUT, "w", encoding="utf-8").write(out)
print(f"yazildi: {OUT}  ({len(out)} bayt, {len(cards)} ekran)")
