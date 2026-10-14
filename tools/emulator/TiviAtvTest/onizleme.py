# Emulator onizlemeleri: veri kaynagi (opkg, OSCam WebIF, tuner, ag) olmayan
# ekranlari ornek veriyle acar; hicbir sistem komutu calistirmaz.
#   from Plugins.Extensions.TiviAtvTest.onizleme import OSCamInfoOnizleme
#   session.open(OSCamInfoOnizleme)

from Screens.CronTimer import CronTimers
from Screens.FlashManager import FlashImage
from Screens.OScamInfo import OSCamEntitlements, OSCamInfo
from Screens.PluginBrowser import PackageAction


class CronTimersOnizleme(CronTimers):
	def __init__(self, session):
		CronTimers.__init__(self, session)
		self.skinName = "CronTimers"

	def installCheck(self):
		for name in ("labstop", "labdisabled"):
			self[name].hide()
		self["labactive"].show()
		self["labrun"].show()
		self["key_yellow"].setText(_("Stop"))
		self["list"].list = [
			("D: 04:30\t/usr/script/settings_backup.sh", ""),
			("W: Sunday 03:00\t/usr/script/epg_refresh.sh", ""),
			("H: 00:15\t/usr/script/picon_sync.sh", ""),
			("M: 1st 05:00\topkg update && opkg upgrade", ""),
		]


class OSCamInfoOnizleme(OSCamInfo):
	ROWS = [
		("s", "root", "n/a", "", "", "", "0000:0000@000000", "n/a\nn/a", "n/a", "08:00:04\n00:00:02", "OK"),
		("h", "root", "n/a", "127.0.0.1", "8888", "http", "0000:0000@000000", "n/a\nn/a", "n/a", "12:41:10\n00:00:01", "OK"),
		("r", "sky_de", "ON", "local", "", "internal", "0085:098C@000000", "Sky Cinema\nSky Deutschland", "1250", "08:00:12\n00:00:01", "CARDOK\n(3 entitlements)"),
		("p", "backup_srv", "OFF", "••••••••", "12000", "cccam\next", "0000:0000@000000", "n/a\nn/a", "n/a", "08:01:40\n00:12:33", "CONNECTED\n(0 of 12 cards)"),
		("c", "livingroom", "OFF", "192.168.1.20", "52314", "cccam", "0085:098C@000000", "Sky Cinema\nSky Deutschland", "sky_de (182 ms)", "09:15:02\n00:00:05", "OK"),
	]

	def __init__(self, session):
		OSCamInfo.__init__(self, session)
		self.skinName = "OSCamInfo"

	def onLayoutFinished(self):
		self["buildinfos"].setText("OSCam: 11.898-@a3f81c2 | srvidfile: /etc/tuxbox/config/oscam.srvid2 | Host: http://127.0.0.1:8888")
		self["extrainfos"].setText("Signed by: oscam-emu (valid)")
		self["timerinfos"].setText("Protocol Time: 14/10/26 - 21:05:12 | Start Time: 14/10/26 - 08:00:01 | OSCam Run Time: 13:05:11")
		self["total"].setText("Total: 1.98 GB")
		self["used"].setText("Used: 612 MB")
		self["free"].setText("Free: 1.38 GB")
		self["buffer"].setText("Buffer: 96 MB")
		self["camname"].setText("OSCam")
		self["virtuell"].setText("Virtuell memory: 38.2 MB")
		self["resident"].setText("Resident Set: 12.7 MB")
		self["outlist"].updateList([(0,) + row for row in self.ROWS])
		self["logtext"].setText("2026/10/14 21:05:10 c (ecm) livingroom (0085:098C): found (182 ms) by sky_de - Sky Cinema\n"
			"2026/10/14 21:05:00 r sky_de [internal] card in slot 1, CAID 098C, ATR ok\n"
			"2026/10/14 21:04:51 s (webif) access from 127.0.0.1")
		self["key_OK"].setText("OK")
		self["key_entitlements"].setText(_("Entitlements"))


class OSCamEntitlementsOnizleme(OSCamEntitlements):
	"""stil: 'default' (yerel kart) ya da 'entitlements' (dis okuyucu)."""
	def __init__(self, session, stil="default"):
		self.stil = stil
		OSCamEntitlements.__init__(self, session, "sky_de" if stil == "default" else "backup_srv")
		self.skinName = "OSCamEntitlements"
		self.loop.stop()

	def onLayoutFinished(self):
		if self.stil == "default":
			rows = [(0, "key", "098C", "000000", "0000000012345678", "0001", "2026-01-01", "2027-01-01", "Sky Deutschland Basic"),
				(0, "key", "098C", "000000", "0000000012345678", "0003", "2026-01-01", "2027-01-01", "Sky Cinema"),
				(0, "key", "098C", "000000", "0000000012345678", "0007", "2026-03-15", "2027-03-15", "Sky Sport")]
		else:
			rows = [(0, "098C", "Videoguard", "1", "2", "1A2B", "3C4D", "000000", "Sky DE", "node1", "1", "2", "1", "1", "0", "0", "2", "0", "0", "0", "1"),
				(0, "0B00", "Conax", "1", "1", "1A2C", "3C4E", "000000, 000001", "Canal Digital", "node2", "0", "1", "0", "1", "0", "0", "1", "0", "0", "0", "0")]
		self._updateEntitlementsUI(rows)
		self["key_detailed"].setText(_("Show details"))


class FlashImageOnizleme(FlashImage):
	def __init__(self, session):
		FlashImage.__init__(self, session, "openatv-8.0-20261014", "/tmp/none.zip")
		self.skinName = "FlashImage"

	def confirmation(self):
		self["header"].setText(_("Downloading image"))
		self["info"].setText("openatv-8.0-20261014_multibox.zip\n312 MB of 486 MB")
		self["progress"].setValue(64)
		self.show()


class PackageActionOnizleme(PackageAction):
	"""Paket listesi (mod 4) ornek verilerle; opkg ve internet denetimi calismaz."""
	def __init__(self, session):
		PackageAction.__init__(self, session, 4)
		self.skinName = ["PackageAction", "PluginAction"]

	def layoutFinished(self):
		e, x, v = self.expandedIcon, self.expandableIcon, self.verticalIcon
		rows = [("extensions", "extensions", "Extensions", None, None, None, e, None, "Extensions", None, None, None)]
		for pkg, name, desc, ver, icon in (
				("enigma2-plugin-extensions-epgimport", "EPGImport", "Import XMLTV EPG data from online sources", "1.9.1", self.installedIcon),
				("enigma2-plugin-extensions-filecommander", "File Commander", "Two-pane file manager with viewer and editor", "3.6", self.upgradableIcon),
				("enigma2-plugin-extensions-iptvplayer", "IPTV Player", "Play IPTV lists and streams", "2.4.0", self.installableIcon),
				("enigma2-plugin-extensions-mediaplayer", "Media Player", "Play audio and video files from your storage", "1.0", self.installIcon)):
			rows.append((pkg, None, None, name, desc, ver, v, icon, "Extensions", True, False, f"{name} ({ver})"))
		for cat, label in (("skins", "Skins"), ("softcams", "Softcams"), ("systemplugins", "System Plugins")):
			rows.append((cat, cat, label, None, None, None, x, None, label, None, None, None))
		self["plugins"].setList(rows)
		self["plugins"].setCurrentIndex(2)
		self["description"].setText("124 packages found.\n1 package marked for install.")
		self["key_green"].setText(_("Install Packages"))
