# TiviATV FHD  -  bos rozet gizleyici
#
# Onceki converter'in metnini aynen gecirir; boolean = "gosterilecek bir sey
# var mi". ConditionalShowHide ile zincirlenince bos rozetin zemini de cizilmez:
#
#   <convert type="PliExtraInfo">ResolutionString</convert>
#   <convert type="TiviAtvText" />
#   <convert type="ConditionalShowHide" />
#
# Bos sayilan: "", "N/A" (codec bilinmiyor), "0x0..." (goruntu boyutu henuz
# gelmedi), "Invalid type" (imajin PliExtraInfo'sunda olmayan tur).
#
# "Crypto": PliExtraInfo CryptoNameCaid'in "Nagra:1830" metninden yalniz sistem
# adi ("Nagra", sifresizde "FTA"). Sifreli kanalda ECM yoksa CAID 0 gelir ve
# "FTA" yanlis olur: gizlenir. IPTV akislarinda sifre bilgisi yok: gizlenir.
#
#   <convert type="PliExtraInfo">CryptoNameCaid</convert>
#   <convert type="TiviAtvText">Crypto</convert>
#   <convert type="ConditionalShowHide" />
#
# "Audio": dogrudan session.CurrentService'e baglanir, calan ses izinin codec'i
# kisa adla (AC3, DD+, AAC, HE-AAC, MPEG, DTS ...). Iz yoksa bos.
#
#   <widget source="session.CurrentService" render="Label" ...>
#       <convert type="TiviAtvText">Audio</convert>
#       <convert type="ConditionalShowHide" />
#
# "Blank": metin hep bos, boolean yine kaynaga gore. Renk tusu cipinin zemini ve
# noktasi icin: tus bosken gizlenir ama kendi yazisini cizmez (yazi rengini
# zemine esitlemek yari saydam renkte ise yaramiyor, yazi opak cikiyor).
#
#   <convert type="TiviAtvText">Blank</convert>
#   <convert type="ConditionalShowHide" />
#
# Kurulum: /usr/lib/enigma2/python/Components/Converter/TiviAtvText.py

from enigma import iServiceInformation

from Components.Converter.Converter import Converter
from Components.Element import cached


class TiviAtvText(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		self.blank = type.strip() == "Blank"
		self.crypto = type.strip() == "Crypto"
		self.audio = type.strip() == "Audio"

	def serviceInfo(self):
		"""Zincirin basindaki CurrentService'in bilgisi (Crypto icin)."""
		source = self.source
		while source is not None and not hasattr(source, "service"):
			source = getattr(source, "source", None)
		service = source and source.service
		return service and service.info()

	def cryptoName(self, text):
		info = self.serviceInfo()
		if not info:
			return ""
		ref = info.getInfoString(iServiceInformation.sServiceref) or ""
		if "://" in ref or "%3a//" in ref.lower():
			return ""
		name = text.split(":")[0].strip()
		if name == "FTA" and info.getInfo(iServiceInformation.sIsCrypted) == 1:
			return ""
		return name

	# (aranan parca, gosterilen ad): sirasi onemli, ozel olan once
	AUDIO = (("truehd", "TrueHD"), ("dts-hd", "DTS-HD"), ("dts", "DTS"), ("e-ac3", "DD+"), ("eac3", "DD+"),
		("ac3+", "DD+"), ("ac-3+", "DD+"), ("digital+", "DD+"), ("digital plus", "DD+"), ("ac3", "AC3"), ("ac-3", "AC3"),
		("dolby digital", "AC3"), ("he-aac", "HE-AAC"), ("heaac", "HE-AAC"), ("aac+", "HE-AAC"), ("aac", "AAC"),
		("mp3", "MP3"), ("mp2", "MP2"), ("mpeg", "MPEG"), ("lpcm", "PCM"), ("pcm", "PCM"), ("opus", "Opus"),
		("vorbis", "Vorbis"), ("flac", "FLAC"), ("wma", "WMA"), ("amr", "AMR"))

	def audioCodec(self):
		service = getattr(self.source, "service", None)
		try:
			audio = service and service.audioTracks()
			if not audio or audio.getNumberOfTracks() <= 0 or audio.getCurrentTrack() < 0:
				return ""
			desc = (audio.getTrackInfo(audio.getCurrentTrack()).getDescription() or "").strip()
		except Exception:
			return ""
		low = desc.lower()
		for part, name in self.AUDIO:
			if part in low:
				return name
		return desc.split(" ")[0][:8].upper() if desc else ""

	def value(self):
		if self.audio:
			return self.audioCodec()
		text = getattr(self.source, "text", None)
		if text is None:  # Boolean kaynak (or. AudioSelection tuslari)
			return "1" if getattr(self.source, "boolean", False) else ""
		text = (text or "").strip()
		if text in ("N/A", _("N/A"), "Invalid type", _("Invalid type")) or text.startswith("0x0"):
			return ""
		if self.crypto and text:
			return self.cryptoName(text)
		return text

	@cached
	def getText(self):
		return "" if self.blank else self.value()

	@cached
	def getBoolean(self):
		return bool(self.value())

	text = property(getText)
	boolean = property(getBoolean)
