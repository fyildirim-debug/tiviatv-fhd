#!/usr/bin/env python3
# Emulator icin ornek kanal listesi, EPG, picon ve test yayini uretir.
#
#   sudo python3 tools/emulator/demo_kanallar.py      (enigma2 KAPALIYKEN)
#
# Yazdiklari:
#   /etc/enigma2/lamedb, bouquets.tv, userbouquet.favourites.tv
#   /etc/enigma2/tiviatv-demo-epg.json   -> TiviAtvTest acilista EPG'ye yukler
#   /etc/enigma2/settings                -> iki satirli liste, son kanal
#   /usr/share/enigma2/picon/*.png       -> duz renkli, kanal adli picon
#   /opt/tivitest/kanal.ts               -> IPTV kanallarinin caldigi test yayini
#
# Uydu kanallari (Turksat 42E) lamedb'den gelir; emulatorde tuner olmadigi
# icin acilmaz ama listede ve EPG'de gorunur. IPTV kanallari 127.0.0.1:8099
# adresinden test yayinini calar (e2-yayin).
import json
import shutil
import subprocess
from pathlib import Path

ETC = Path("/etc/enigma2")
PICON = Path("/usr/share/enigma2/picon")
STREAM_DIR = Path("/opt/tivitest")
NS = 0x01A40000  # 42.0E
STREAM = "http%3a//127.0.0.1%3a8099/kanal.ts"

# ad, saglayici, tur (dvb/iptv), picon rengi
CHANNELS = [
	("TRT 1", "TRT", "dvb", "#c8102e"),
	("Show TV", "Ciner", "dvb", "#e4002b"),
	("Star TV", "Dogus", "dvb", "#1d4f91"),
	("ATV", "Turkuvaz", "dvb", "#0055a5"),
	("Kanal D", "Demiroren", "iptv", "#00843d"),
	("NOW", "Disney", "iptv", "#111111"),
	("TV8", "Acun Medya", "iptv", "#f39200"),
	("TRT Spor", "TRT", "iptv", "#00a0df"),
	("TRT Belgesel", "TRT", "iptv", "#5b8c32"),
	("NTV", "Dogus", "iptv", "#d6001c"),
	("CNN Turk", "Demiroren", "iptv", "#cc0000"),
	("TRT Cocuk", "TRT", "iptv", "#7ac143"),
	("Cartoon Network", "Warner", "iptv", "#222222"),
	("National Geographic", "Disney", "iptv", "#ffcc00"),
	("TLC", "Discovery", "iptv", "#5a2d82"),
	("DMAX", "Discovery", "iptv", "#2b2b2b"),
]

# baslik, kisa aciklama, uzun aciklama, dakika, tur (DVB content nibble)
SHOWS = [
	("Sabah Kusagi", "Gunaydin Turkiye", "Gundem, hava durumu ve konuk sohbetleriyle canli sabah programi.", 90, 0x10),
	("Ana Haber Bulteni", "Gunun onemli gelismeleri", "Yurt ici ve yurt disindan son dakika haberleri, ekonomi ve spor.", 60, 0x20),
	("Belgesel: Anadolu'nun Kuslari", "Doga belgeseli", "Goc yollarindaki sulak alanlarda dort mevsim boyunca cekilen belgesel.", 50, 0x90),
	("Super Lig Ozeti", "Haftanin tum golleri", "Haftanin maclarindan goller, pozisyonlar ve yorumlar.", 45, 0x40),
	("Gece Sinemasi: Son Tren", "Gerilim, 2019", "Bir kis gecesi son trene binen yabancilarin hikayesi. Yonetmen: A. Kaya.", 110, 0x10),
	("Mutfak Atolyesi", "Ev yemekleri", "Sefler ozel tariflerini adim adim anlatiyor.", 40, 0xa0),
	("Ekonomi Masasi", "Piyasalarda gun sonu", "Borsa, doviz ve emtia piyasalarinda gunun degerlendirmesi.", 30, 0x20),
	("Cizgi Dunyasi", "Cocuk programi", "Okul oncesi cocuklar icin egitici cizgi filmler.", 25, 0x50),
	("Dizi: Mavi Liman", "12. Bolum", "Liman kasabasinda iki ailenin yillardir suren rekabeti yeni bir sir ile alevleniyor.", 120, 0x10),
	("Teknoloji Gundemi", "Haftanin yenilikleri", "Yeni cihazlar, yazilimlar ve bilim dunyasindan haberler.", 35, 0x90),
]


def dvb_ref(sid, tsid, onid):
	return "1:0:1:%X:%X:%X:%X:0:0:0:" % (sid, tsid, onid, NS)


def write_lists():
	trans, services, bouquet, epg = [], [], [], []
	for i, (name, prov, kind, _color) in enumerate(CHANNELS):
		sid, tsid, onid = 0x100 + i, 1 + i // 4, 1
		ref = dvb_ref(sid, tsid, onid)
		if kind == "dvb":
			key = "%08x:%04x:%04x" % (NS, tsid, onid)
			if key not in [t[0] for t in trans]:
				trans.append((key, "\ts %d:27500000:%d:3:420:2:0:1:2:0:2" % (11054000 + tsid * 40000, tsid % 2)))
			services.append("%04x:%08x:%04x:%04x:1:0\n%s\np:%s\n" % (sid, NS, tsid, onid, name, prov))
			bouquet.append("#SERVICE %s\n" % ref)
		else:
			# IPTV: DVB kimligi (sid/tsid/onid) EPG ve picon eslesmesi icin
			bouquet.append("#SERVICE 4097:0:1:%X:%X:%X:%X:0:0:0:%s:%s\n" % (sid, tsid, onid, NS, STREAM, name))
		shows = SHOWS[i % len(SHOWS):] + SHOWS[:i % len(SHOWS)]
		epg.append({"ref": ref, "programs": [list(s) for s in shows * 2]})

	lamedb = ["eDVB services /4/\ntransponders\n"]
	for key, line in trans:
		lamedb.append("%s\n%s\n/\n" % (key, line))
	lamedb.append("end\nservices\n")
	lamedb.extend(services)
	lamedb.append("end\nHave a lot of bugs!\n")
	(ETC / "lamedb").write_text("".join(lamedb), encoding="utf-8")
	(ETC / "bouquets.tv").write_text(
		"#NAME User - Bouquets (TV)\n"
		"#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET \"userbouquet.favourites.tv\" ORDER BY bouquet\n",
		encoding="utf-8")
	(ETC / "userbouquet.favourites.tv").write_text("#NAME Favoriler (TV)\n" + "".join(bouquet), encoding="utf-8")
	(ETC / "tiviatv-demo-epg.json").write_text(json.dumps(epg, ensure_ascii=False, indent=1), encoding="utf-8")
	# acilis kanali: ilk IPTV kanali (uydu kanallari emulatorde calmaz)
	return next(b for b in bouquet if b.startswith("#SERVICE 4097")).split(" ", 1)[1].strip()


def write_settings(first_ref):
	path = ETC / "settings"
	keep = [l for l in path.read_text(encoding="utf-8").splitlines() if l and not l.startswith((
		"config.usage.servicelist_twolines=", "config.usage.serviceitems_per_page_twolines=",
		"config.tv.lastservice=", "config.tv.lastroot=", "config.skin.primary_skin="))]
	root = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet;' \
	       '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet;'
	keep += [
		"config.skin.primary_skin=TiviAtv-FHD/skin.xml",
		"config.usage.servicelist_twolines=true",
		"config.usage.serviceitems_per_page_twolines=10",
		"config.tv.lastroot=" + root,
		"config.tv.lastservice=" + first_ref,
	]
	path.write_text("\n".join(keep) + "\n", encoding="utf-8")


def write_picons():
	from PIL import Image, ImageDraw, ImageFont
	PICON.mkdir(parents=True, exist_ok=True)
	font = next((f for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",) if Path(f).exists()), None)
	for i, (name, _p, _k, color) in enumerate(CHANNELS):
		img = Image.new("RGBA", (220, 132), (0, 0, 0, 0))
		d = ImageDraw.Draw(img)
		d.rounded_rectangle((6, 14, 214, 118), radius=16, fill=color)
		size = 34 if len(name) < 9 else 24 if len(name) < 14 else 18
		f = ImageFont.truetype(font, size) if font else ImageFont.load_default()
		w = d.textlength(name, font=f)
		d.text(((220 - w) / 2, 66 - size * 0.6), name, font=f, fill="white")
		ref = dvb_ref(0x100 + i, 1 + i // 4, 1)
		img.save(PICON / (ref.rstrip(":").replace(":", "_") + ".png"))


def write_stream():
	STREAM_DIR.mkdir(parents=True, exist_ok=True)
	out = STREAM_DIR / "kanal.ts"
	if out.exists() or not shutil.which("ffmpeg"):
		return
	subprocess.run([
		"ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=25",
		"-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000", "-t", "120",
		"-c:v", "libx264", "-preset", "ultrafast", "-b:v", "800k", "-g", "50",
		"-c:a", "aac", "-b:a", "96k", "-f", "mpegts", str(out)], check=True)


if __name__ == "__main__":
	if subprocess.run(["pgrep", "-x", "enigma2"], capture_output=True).returncode == 0:
		raise SystemExit("once enigma2'yi durdur (kapanista lamedb ve settings uzerine yazilir)")
	first = write_lists()
	write_settings(first)
	write_picons()
	write_stream()
	print("%d kanal yazildi, ilk kanal: %s" % (len(CHANNELS), first))
