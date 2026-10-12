# TiviATV FHD  -  softcam ECM bilgisi (OSCam, CCcam, ...) /tmp/ecm.info'dan
#
#   <convert type="TiviAtvEcm" />
#       -> "Irdeto 0604 · my_reader · newcamd · 1 hop · 0.214 s"
#
# Kanal sifreli degilse, ecm.info yoksa ya da Kullanim ayarlarinda sifre
# bilgisi (config.usage.show_cryptoinfo) kapaliysa bos doner; boolean da ayni
# kosula bakar (ConditionalShowHide). Softcam'in "sunucu adini gizle" ayari
# acikken (config.softcam.hideServerName) sunucu adresi "•••" olarak gosterilir.
#
# Kurulum: /usr/lib/enigma2/python/Components/Converter/TiviAtvEcm.py

from os import stat
from re import IGNORECASE, search

from enigma import iServiceInformation

from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from Components.Element import cached

ECM_INFO = "/tmp/ecm.info"
ADDRESS = r"\d{1,3}(\.\d{1,3}){3}|\w[\w-]*(\.[\w-]+)+|:\d{2,5}\b"  # IP, alan adi, :port
SOURCE_MAX, PROTOCOL_MAX = 24, 16  # uzun okuyucu / sunucu adi satirin basini itmesin

# CAID ust bayti -> sistem adi (ecm.info'da "system:" satiri yoksa)
SYSTEMS = {
	0x01: "Seca", 0x05: "Viaccess", 0x06: "Irdeto", 0x09: "Videoguard", 0x0B: "Conax",
	0x0D: "CryptoWorks", 0x0E: "PowerVU", 0x10: "Tandberg", 0x17: "BetaCrypt", 0x18: "Nagravision",
	0x26: "BISS", 0x4A: "DRE", 0x55: "Bulcrypt", 0x56: "Verimatrix",
}


def setting(path, default):
	"""config.a.b degeri; imajda yoksa varsayilan."""
	try:
		from Components.config import config
		node = config
		for part in path.split("."):
			node = getattr(node, part)
		return node.value
	except Exception:
		return default


def readEcmInfo():
	"""ecm.info'yu {anahtar: deger} olarak okur (anahtarlar kucuk harf)."""
	info = {}
	try:
		with open(ECM_INFO, errors="replace") as handle:
			text = handle.read()
	except OSError:
		return info
	for line in text.splitlines():
		key, sep, value = line.partition(":")
		if sep and key.strip():
			info[key.strip().lower()] = value.strip()
	if "caid" not in info:  # gbox / CCcam: "... CaID 0x1802, pid ..."
		found = search(r"caid\s*:?\s*(0x[0-9a-f]{3,4})", text, IGNORECASE)
		if found:
			info["caid"] = found.group(1)
	return info


def shorten(text, limit):
	return text if len(text) <= limit else text[:limit - 1].rstrip(" .:-_") + "…"


def ecmText(info, hideServer=False):
	"""ecm.info sozlugunden tek satir; bilgi yoksa bos."""
	if not info:
		return ""
	caid = system = ""
	try:
		value = int(info.get("caid", "").split()[0], 16)
		caid = "%04X" % value
		system = SYSTEMS.get(value >> 8, "")
	except (ValueError, IndexError):
		pass
	system = info.get("system", system)
	key = next((k for k in ("reader", "source", "address", "decode", "from") if info.get(k)), "")
	source = info.get(key, "")
	# "address"/"from" hep sunucudur; digerlerinde IP ya da ad:port geciyorsa gizlenir
	if hideServer and (key in ("address", "from") or search(ADDRESS, source)):
		source = "•••"
	protocol = info.get("protocol") or info.get("using") or ""
	if protocol.lower() == source.lower():
		protocol = ""
	source, protocol = shorten(source, SOURCE_MAX), shorten(protocol, PROTOCOL_MAX)
	hops = info.get("hops", "").strip()
	hops = ("%s hop" % hops if hops == "1" else "%s hops" % hops) if hops.isdigit() and hops != "0" else ""
	seconds = info.get("ecm time", "").split()
	timing = ""
	if seconds:
		try:
			value = float(seconds[0].replace(",", "."))
			timing = "%.3f s" % (value / 1000.0 if value > 30 else value)  # bazi softcam'ler ms yazar
		except ValueError:
			pass
	parts = [" ".join(x for x in (system, caid) if x), source, protocol, hops, timing]
	return "  ·  ".join(x for x in parts if x)


class TiviAtvEcm(Poll, Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 1000
		self.poll_enabled = True
		self.mtime = None
		self.info = {}

	def crypted(self):
		service = self.source.service
		info = service and service.info()
		return bool(info) and info.getInfo(iServiceInformation.sIsCrypted) == 1

	def current(self):
		if setting("usage.show_cryptoinfo", 1) in (0, False) or not self.crypted():
			return ""
		try:
			mtime = stat(ECM_INFO).st_mtime
		except OSError:
			self.mtime, self.info = None, {}
			return ""
		if mtime != self.mtime:  # dosya degismedikce yeniden okunmaz
			self.mtime, self.info = mtime, readEcmInfo()
		return ecmText(self.info, bool(setting("softcam.hideServerName", False)))

	@cached
	def getText(self):
		return self.current()

	text = property(getText)

	@cached
	def getBoolean(self):
		return bool(self.current())

	boolean = property(getBoolean)
