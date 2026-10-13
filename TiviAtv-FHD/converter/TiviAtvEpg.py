# TiviATV FHD  -  kanal listesi EPG paneli: secili kanalin siradaki programlari
#
#   <convert type="TiviAtvEpg">Panel</convert>       boolean: panel acik mi (ConditionalShowHide)
#   <convert type="TiviAtvEpg">Heading</convert>     panel basligi ("LATER"), panel kapaliyken bos
#   <convert type="TiviAtvEpg">Time1</convert> ...   Time1..Time5: NEXT'ten sonraki programlarin saati
#   <convert type="TiviAtvEpg">Title1</convert> ...  Title1..Title5: ayni programlarin adi
#   <convert type="TiviAtvEpg">Prime</convert>       boolean: primetime acik ve o saatte program var
#   <convert type="TiviAtvEpg">PrimeTime</convert>   "PRIMETIME" (cip; program yoksa bos)
#   <convert type="TiviAtvEpg">PrimeTitle</convert>  "20:20  Ad": ayarli saatte yayinlanan program
#
# Kanal kartinda simdiki (NOW) ve sonraki (NEXT) program zaten var; panel
# onlardan sonraki 5 programi gosterir, ikisiyle birlikte 7 program.
#
# Kaynak ChannelSelection'in ServiceEvent'i (listede secili kanal). Panel
# kapaliyken metinler bos, boolean'lar False; ayar degisince ekran hemen
# guncellenir. Ayarlar "TiviATV Settings" eklentisinden: settings().
#
# Kurulum: /usr/lib/enigma2/python/Components/Converter/TiviAtvEpg.py

from time import localtime, mktime, strftime, time

from enigma import eEPGCache

from Components.config import ConfigSelection, ConfigSubsection, ConfigYesNo, config
from Components.Converter.Converter import Converter
from Components.Element import cached

ROWS = 5
_cache = {}  # {servis: (zaman dilimi, olaylar)}: 10 satir ayni sorguyu paylasir
PRIMETIMES = ("off", "19:00", "19:30", "20:00", "20:15", "20:30", "21:00", "21:30", "22:00")


def settings():
	"""config.plugins.TiviAtv: converter, renderer ve eklenti ayni ayarlari kullanir."""
	if not hasattr(config.plugins, "TiviAtv"):
		config.plugins.TiviAtv = ConfigSubsection()
		config.plugins.TiviAtv.epgPanel = ConfigYesNo(default=False)
		config.plugins.TiviAtv.primetime = ConfigSelection(default="20:15", choices=[(x, _("Off") if x == "off" else x) for x in PRIMETIMES])
		config.plugins.TiviAtv.scroll = ConfigYesNo(default=True)
	return config.plugins.TiviAtv


class TiviAtvEpg(Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type.strip()
		self.options = settings()
		self.epgcache = eEPGCache.getInstance()
		for item in (self.options.epgPanel, self.options.primetime):
			item.addNotifier(self.configChanged, initial_call=False)

	def configChanged(self, configElement):
		self.changed((self.CHANGED_ALL,))

	def panel(self):
		return bool(self.options.epgPanel.value)

	def primeEnabled(self):
		return self.panel() and self.options.primetime.value != "off"

	def upcoming(self):
		"""NEXT'ten sonraki ROWS program: [(baslangic, ad)]."""
		if not self.panel():
			return []
		service = self.source and self.source.service
		if not service or not self.epgcache:
			return []
		ref, now = service.toString(), time()
		slot, events = _cache.get(ref, (None, None))
		if slot != int(now // 30):
			try:
				events = self.epgcache.lookupEvent(["BT", (ref, 0, -1, 1440)]) or []
			except Exception:
				events = []
			_cache.clear()
			_cache[ref] = (int(now // 30), events)
		later = [(begin, title) for begin, title in events if begin and begin > now]
		return later[1:ROWS + 1]  # ilki NEXT, kartta

	def primeEvent(self):
		"""Ayarli saatte (bugun; bitmisse yarin) yayinlanan program: (baslangic, ad)."""
		if not self.primeEnabled():
			return None
		service = self.source and self.source.service
		if not service or not self.epgcache:
			return None
		hour, minute = (int(x) for x in self.options.primetime.value.split(":"))
		lt = localtime()
		start = mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, hour, minute, 0, 0, 0, -1))
		for at in (start, start + 86400):
			try:
				found = self.epgcache.lookupEvent(["BDT", (service.toString(), 0, int(at))]) or []
			except Exception:
				found = []
			for begin, duration, title in found:
				if begin and title and begin + (duration or 0) > time():
					return begin, title
		return None

	@cached
	def getText(self):
		kind, index = self.type.rstrip("0123456789"), self.type[len(self.type.rstrip("0123456789")):]
		if kind in ("Time", "Title") and index:
			rows = self.upcoming()
			row = int(index) - 1
			if 0 <= row < len(rows):
				begin, title = rows[row]
				return strftime("%H:%M", localtime(begin)) if kind == "Time" else title
			return ""
		if self.type == "Heading":
			return _("LATER") if self.panel() else ""
		if self.type == "PrimeTime":
			return "PRIMETIME" if self.primeEvent() else ""
		if self.type == "PrimeTitle":
			event = self.primeEvent()
			return "%s  %s" % (strftime("%H:%M", localtime(event[0])), event[1]) if event else ""
		return ""

	text = property(getText)

	@cached
	def getBoolean(self):
		if self.type in ("Prime", "PrimeTime", "PrimeTitle"):  # o saatte program yoksa cip de gizli
			return self.primeEvent() is not None
		return self.panel()

	boolean = property(getBoolean)

