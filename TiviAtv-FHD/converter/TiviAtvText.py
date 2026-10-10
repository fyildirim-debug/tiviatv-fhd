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
# Kurulum: /usr/lib/enigma2/python/Components/Converter/TiviAtvText.py

from Components.Converter.Converter import Converter
from Components.Element import cached


class TiviAtvText(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)

	@cached
	def getText(self):
		text = (self.source.text or "").strip()
		if text in ("N/A", _("N/A")) or text.startswith("0x0"):
			return ""
		return text

	@cached
	def getBoolean(self):
		return bool(self.getText())

	text = property(getText)
	boolean = property(getBoolean)
