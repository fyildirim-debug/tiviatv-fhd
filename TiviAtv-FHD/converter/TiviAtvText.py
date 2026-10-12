# TiviATV FHD  -  bos rozet gizleyici
#
# Onceki converter'in metnini aynen gecirir; boolean = "gosterilecek bir sey
# var mi". ConditionalShowHide ile zincirlenince bos rozetin zemini de cizilmez:
#
#   <convert type="PliExtraInfo">CurrentCrypto</convert>
#   <convert type="TiviAtvText" />
#   <convert type="ConditionalShowHide" />
#
# Bos sayilan: "", "N/A" (codec bilinmiyor), "0x0..." (goruntu boyutu henuz
# gelmedi). IPTV'de sifreleme bilgisi hic olmadigi icin sifre rozeti hep bostu.
#
# "Blank": metin hep bos, boolean yine kaynaga gore. Renk tusu cipinin zemini ve
# noktasi icin: tus bosken gizlenir ama kendi yazisini cizmez (yazi rengini
# zemine esitlemek yari saydam renkte ise yaramiyor, yazi opak cikiyor).
#
#   <convert type="TiviAtvText">Blank</convert>
#   <convert type="ConditionalShowHide" />
#
# Kurulum: /usr/lib/enigma2/python/Components/Converter/TiviAtvText.py

from Components.Converter.Converter import Converter
from Components.Element import cached


class TiviAtvText(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		self.blank = type.strip() == "Blank"

	def value(self):
		text = getattr(self.source, "text", None)
		if text is None:  # Boolean kaynak (or. AudioSelection tuslari)
			return "1" if getattr(self.source, "boolean", False) else ""
		text = (text or "").strip()
		if text in ("N/A", _("N/A")) or text.startswith("0x0"):
			return ""
		return text

	@cached
	def getText(self):
		return "" if self.blank else self.value()

	@cached
	def getBoolean(self):
		return bool(self.value())

	text = property(getText)
	boolean = property(getBoolean)
