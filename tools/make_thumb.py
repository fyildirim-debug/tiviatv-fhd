# Skin secicideki prev.png'yi uretir: emulatorde alinmis kanal listesi
# goruntusunu kucultur. Elle cizim yok; ekran ne ise onizleme o.
# Skin secicideki kutu 436 px genis; 640x360 ve 256 renk yeterli, dosya kucuk kalir.
#
#   python3 tools/emulator/ekranlar.py --kare kare.jpg .cache/ekranlar channelselection
#   python3 tools/make_thumb.py [.cache/ekranlar/channelselection.png]
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".cache" / "ekranlar" / "channelselection.png"
OUT = ROOT / "TiviAtv-FHD" / "prev.png"

if not SRC.exists():
	sys.exit("goruntu yok: %s (once tools/emulator/ekranlar.py)" % SRC)
im = Image.open(SRC).convert("RGB").resize((640, 360), Image.LANCZOS)
im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(OUT, optimize=True)
print("yazildi: %s" % OUT)
