# TiviATV FHD  -  emulator test kancasi  (KUTUYA KURULMAZ)
#
# Yalnizca PC emulatorunde kullanilir:
#   - /tmp/e2py.cmd dosyasindaki Python kodunu enigma2'nin icinde calistirir
#     (session hazir gelir), sonucu /tmp/e2py.out'a yazar. tools/emulator/e2-py
#     bunu kullanir; ekranlar menude gezinmeden dogrudan acilir.
#   - demo_kanallar.py'nin yazdigi EPG'yi acilista simdiki saate gore yukler.

import json
import traceback
from os import path, remove, rename
from time import time

from enigma import eEPGCache, eTimer

from Plugins.Plugin import PluginDescriptor

CMD = "/tmp/e2py.cmd"
OUT = "/tmp/e2py.out"
EPG = "/etc/enigma2/tiviatv-demo-epg.json"

runner = None


def loadEpg():
	if not path.exists(EPG):
		return 0
	with open(EPG, encoding="utf-8") as fd:
		channels = json.load(fd)
	cache = eEPGCache.getInstance()
	now = int(time())
	count = 0
	for i, ch in enumerate(channels):
		# her kanal farkli bir anda baslasin: simdiki program ortada olsun
		start = now - now % 1800 - 3600 - (i % 4) * 900
		events = []
		for title, short, extended, minutes, genre in ch["programs"]:
			events.append((start, minutes * 60, title, short, extended, genre))
			start += minutes * 60
		cache.importEvents(ch["ref"], events)
		count += len(events)
	return count


class Runner:
	def __init__(self, session):
		self.session = session
		self.env = {"session": session}
		self.timer = eTimer()
		self.timer.callback.append(self.poll)
		self.timer.start(250, False)
		try:
			print("[TiviAtvTest] EPG olaylari: %d" % loadEpg())
		except Exception:
			traceback.print_exc()

	def poll(self):
		if not path.exists(CMD):
			return
		with open(CMD, encoding="utf-8") as fd:
			code = fd.read()
		remove(CMD)
		lines = []
		self.env["out"] = lambda *args: lines.append(" ".join(str(a) for a in args))
		try:
			exec(code, self.env)
			result = "OK\n"
		except Exception:
			result = "HATA\n" + traceback.format_exc()
		with open(OUT + ".tmp", "w", encoding="utf-8") as fd:
			fd.write(result + "\n".join(lines) + "\n")
		rename(OUT + ".tmp", OUT)


def sessionstart(reason, session=None, **kwargs):
	global runner
	if reason == 0 and session and runner is None:
		runner = Runner(session)


def Plugins(**kwargs):
	return [PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart)]
