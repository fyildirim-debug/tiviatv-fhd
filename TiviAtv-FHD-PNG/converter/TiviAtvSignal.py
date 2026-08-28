# TiviATV FHD  -  sinyal (DVB) / akis hizi (IPTV)
#
# Kaynak: session.FrontendStatus  -  IPTV servisinde snr/agc None olur,
# ayrimi bu saglar.
#
# Skinde kullanilan tipler:
#   SNR      -> Progress icin deger (0-100)
#   AGC      -> Progress icin deger (0-100)
#   SNRText  -> "%86"        (IPTV'de bos)
#   AGCText  -> "%76"        (IPTV'de bos)
#   Speed    -> "3.76 Mb/s"  (DVB'de bos)
#   IsDVB    -> ConditionalShowHide icin bool
#   (argumansiz) -> "SNR %86  ·  AGC %76" ya da "3.76 Mb/s"
#
# Kurulum: /usr/lib/enigma2/python/Components/Converter/TiviAtvSignal.py

from time import time

from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from Components.Element import cached

NET_PREFIXES = ("eth", "wlan", "ra", "wifi")

SUMMARY, SNR, AGC, SNR_TEXT, AGC_TEXT, SPEED, IS_DVB = range(7)

MODES = {
	"SNR": SNR,
	"AGC": AGC,
	"SNRText": SNR_TEXT,
	"AGCText": AGC_TEXT,
	"Speed": SPEED,
	"IsDVB": IS_DVB,
}


class TiviAtvSignal(Poll, Converter, object):
	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 1000
		self.poll_enabled = True
		self.mode = MODES.get(type, SUMMARY)
		self.last = None
		self.speed = None

	def percent(self, name):
		"""snr / agc -> 0-100, tuner yoksa None."""
		raw = getattr(self.source, name, None)
		return None if raw is None else raw * 100 // 65536

	def netSpeed(self):
		"""Mbit/s - iki olcum arasindaki rx farkindan.

		IPTV akisi patlamalar halinde gelir; kisa pencerede olcum sifira
		yakin cikabiliyor. Iki saniyelik pencere ve son iki olcumun
		ortalamasi degeri oturtuyor. Pencere dolmadan son deger doner.
		"""
		now = time()
		if self.last and now - self.last[0] < 2.0:
			return self.speed
		total = 0
		try:
			with open("/proc/net/dev") as fd:
				for line in fd:
					if ":" not in line:
						continue
					name, rest = line.split(":", 1)
					if not name.strip().startswith(NET_PREFIXES):
						continue
					total += int(rest.split()[0])
		except (OSError, ValueError, IndexError):
			return None
		prev = self.last
		self.last = (now, total)
		if not prev or total < prev[1]:
			self.speed = None
		else:
			mbits = (total - prev[1]) * 8.0 / (now - prev[0]) / 1000000.0
			self.speed = mbits if self.speed is None else (self.speed + mbits) / 2.0
		return self.speed

	@cached
	def getText(self):
		snr = self.percent("snr")
		if self.mode == SNR_TEXT:
			return "" if snr is None else "%%%d" % snr
		if self.mode == AGC_TEXT:
			agc = self.percent("agc")
			return "" if snr is None or agc is None else "%%%d" % agc
		if self.mode == SPEED:
			if snr is not None:
				return ""
			speed = self.netSpeed()
			return "" if speed is None else "%.2f Mb/s" % speed
		if self.mode == SUMMARY:
			if snr is not None:
				return "SNR %%%d  ·  AGC %%%d" % (snr, self.percent("agc") or 0)
			speed = self.netSpeed()
			return "" if speed is None else "%.2f Mb/s" % speed
		return ""

	@cached
	def getValue(self):
		value = self.percent("snr" if self.mode == SNR else "agc")
		return value or 0

	@cached
	def getBoolean(self):
		return self.percent("snr") is not None

	text = property(getText)
	value = property(getValue)
	boolean = property(getBoolean)
	range = 100
