#!/usr/bin/env python3
# Emulatorde ekranlari tek tek acip goruntusunu alir (enigma2 calisirken).
#
#   python3 tools/emulator/ekranlar.py [--kare video.jpg] [klasor] [ekran ...]
#
# Ekranlar menude gezinmeden TiviAtvTest kancasiyla (e2-py) dogrudan acilir,
# goruntu e2-ekran ile enigma2'nin kendi cerceve belleginden alinir. Her
# ekrandan sonra InfoBar'a donulur. Ekran adi verilmezse hepsi cekilir.
# --kare: OSD saydam yerlerine alfasiyla konan "yayin" karesi; kutuda OSD'yi
# goruntu katmaninin ustune donanim birlestirir, emulatorde video yok.
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARGS = sys.argv[1:]
KARE = []
if ARGS[:1] == ["--kare"]:
	KARE, ARGS = [str(Path(ARGS[1]).resolve())], ARGS[2:]
OUT = Path(ARGS[0]) if ARGS else HERE.parents[1] / ".cache" / "ekranlar"
ONLY = set(ARGS[1:])

IB = "from Screens.InfoBar import InfoBar\nib = InfoBar.instance\n"

# ad: (acma kodu ya da adim listesi, sonra basilacak tuslar, bekleme sn)
SCREENS = {
	"infobar": ("ib.show()", [], 1.5),
	# InfoBar acikken OK: 2. InfoBar ayari "2" (varsayilan "1" EventView acar)
	"secondinfobar": (["from Components.config import config\nconfig.usage.show_second_infobar.value = '2'\nib.toggleShow()",
	                   "ib.toggleShow()"], [], 1.5),
	"channelselection": ("ib.openServiceList()", [], 2),
	# modal ekran ancak modal bir ekranin ustune acilir: ikinci adimda
	"channelcontextmenu": (["ib.openServiceList()",
	                        "from Screens.ChannelSelection import ChannelContextMenu\n"
	                        "session.open(ChannelContextMenu, ib.servicelist)"], [], 2),
	"epgselection": ("ib.openSingleServiceEPG()", [], 2),
	"graphicalepg": ("ib.openGraphEPG()", [], 3),
	"multiepg": ("ib.openMultiServiceEPG()", [], 3),
	"eventview": ("ib.openEventView()", [], 2),
	"menu": ("ib.showMainMenu()", [], 1.5),
	"setup": ("from Screens.Setup import Setup\nsession.open(Setup, 'ChannelSelection')", [], 1.5),
	"skinselection": ("from Screens.SkinSelection import SkinSelection\nsession.open(SkinSelection)", [], 2),
	"messagebox": ("from Screens.MessageBox import MessageBox\n"
	               "session.open(MessageBox, 'Save the channel list?\\nChanges will be written to the box.', MessageBox.TYPE_YESNO)", [], 1.5),
	"choicebox": ("from Screens.ChoiceBox import ChoiceBox\n"
	              "session.open(ChoiceBox, title='GUI typeface', list=[(n, n) for n in ('Inter   (4 weights)   -  active', 'Geist   (4 weights)', 'Barlow   (4 weights)', 'Sony_Sketch_Bold_205')])", [], 1.5),
	"audioselection": ("ib.audioSelection()", [], 2),
	"volume": ("from Components.VolumeControl import VolumeControl\nVolumeControl.instance.volUp()", [], 0.8),
	"mute": ("from Components.VolumeControl import VolumeControl\nVolumeControl.instance.volMute()", [], 0.8),
	# InfoBar.keyNumberGlobal oynatilan akis sarilabiliyorsa sarar; ekran dogrudan acilir
	"numberzap": ("from Screens.InfoBarGenerics import NumberZap\nfrom Components.config import config\nconfig.usage.numzappicon.value = True\nsession.open(NumberZap, 7, ib.searchNumber)", [], 0.6),
	"pluginbrowser": ("from Screens.PluginBrowser import PluginBrowser\nsession.open(PluginBrowser)", [], 2),
	# OpenViX benzetimi: ayni skin ekrani, klasik PluginList (name="list") ve
	# Button renk tuslari (objectTypes ile secilen ikinci tus seti)
	"pluginbrowser-vix": ("from Screens.Screen import Screen\nfrom Components.ActionMap import ActionMap\n"
	                      "from Components.Button import Button\nfrom Components.PluginComponent import plugins\n"
	                      "from Components.PluginList import PluginList, PluginEntryComponent\nfrom Plugins.Plugin import PluginDescriptor\n"
	                      "class VixPluginBrowser(Screen):\n"
	                      "\tdef __init__(self, session):\n"
	                      "\t\tScreen.__init__(self, session)\n"
	                      "\t\tself.skinName = 'PluginBrowser'\n"
	                      "\t\tself.setTitle('Plugin Browser')\n"
	                      "\t\tself['key_red'] = Button('Remove plugins')\n"
	                      "\t\tself['key_green'] = Button('Download plugins')\n"
	                      "\t\tself['key_yellow'] = Button('User installed plugins')\n"
	                      "\t\tself['list'] = PluginList([])\n"
	                      "\t\tself['actions'] = ActionMap(['OkCancelActions'], {'ok': self.close, 'cancel': self.close})\n"
	                      "\t\tself.onLayoutFinish.append(self.fill)\n"
	                      "\tdef fill(self):\n"
	                      "\t\twidth = self['list'].instance.size().width()\n"
	                      "\t\tself['list'].setList([PluginEntryComponent(p, width) for p in plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)])\n"
	                      "session.open(VixPluginBrowser)", [], 2),
	# skinde henuz olmayan, sik acilan ekranlar
	"inputbox": ("from Screens.InputBox import InputBox\nsession.open(InputBox, title='Enter the channel name', text='Kanal D')", [], 1.5),
	"pininput": ("from Screens.InputBox import PinInput\nfrom Components.config import config\nsession.open(PinInput, pinList=[1234], triesEntry=config.ParentalControl.retries.servicepin, title='Enter your PIN', windowTitle='Parental control')", [], 1.5),
	"virtualkeyboard": ("from Screens.VirtualKeyBoard import VirtualKeyBoard\nsession.open(VirtualKeyBoard, title='Search', text='blue harbour')", [], 2),
	"timereditlist": ("from RecordTimer import RecordTimerEntry\nfrom ServiceReference import ServiceReference\n"
	                  "from time import time\nrt = session.nav.RecordTimer\n"
	                  "if not rt.timer_list:\n"
	                  "\tfor i, (ref, name) in enumerate((('1:0:1:100:1:1:1A40000:0:0:0:', 'Evening News'), ('1:0:1:102:1:1:1A40000:0:0:0:', 'Late Movie: The Last Train'))):\n"
	                  "\t\tt = int(time()) + 3600 * (i + 1)\n"
	                  "\t\trt.record(RecordTimerEntry(ServiceReference(ref), t, t + 3000, name, 'Sample timer', None))\n"
	                  "from Screens.TimerEdit import TimerEditList\nsession.open(TimerEditList)", [], 2),
	"console": ("from Screens.Console import Console\nsession.open(Console, title='Installing package', cmdlist=['echo opkg update; echo Downloading feed...; echo Updated source; echo Package installed.'])", [], 3),
	"textbox": ("from Screens.TextBox import TextBox\nsession.open(TextBox, text=open('/etc/image-version').read() * 6, title='Image information', skinName='TextBox')", [], 1.5),
	# skinName verilmezse TextBox ['None', 'TextBox'] listesi kurar; openATV skin.py
	# bu listeyi loglarken (", ".join) coker ve ekran widget'siz kalir (upstream hatasi)
	"information": ("from Screens.Information import InformationDistribution\nsession.open(InformationDistribution)", [], 3),
	"movieselection": ("from Screens.MovieSelection import MovieSelection\nsession.open(MovieSelection)", [], 3),
	"movieplayer": (["from Screens.InfoBar import MoviePlayer\nfrom enigma import eServiceReference\n"
	                 "ref = eServiceReference(4097, 0, '/opt/tivitest/kanal.ts')\nref.setName('Late Movie: The Last Train')\n"
	                 "session.open(MoviePlayer, ref)",
	                 "session.current_dialog.pauseService()"], [], 3),  # durum ikonu: duraklat
	# Bekleme / Yeniden baslat > MultiBoot Manager (emulatorde yuva yok: liste yukleniyor / bos)
	"multibootmanager": (["from Screens.MultiBootManager import MultiBootManager\nsession.open(MultiBootManager)",
	                      "from Components.ChoiceList import ChoiceEntryComponent\nd = session.current_dialog\n"
	                      "d['slotlist'].setList([ChoiceEntryComponent('', (text, n)) for n, text in enumerate(("
	                      "'Slot 1:  openATV 7.6 (2026-10-10)  -  Current', 'Slot 2:  OpenViX 6.7.012 (2026-09-28)', "
	                      "'Slot 3:  OpenPLi 9.1 (2026-08-14)', 'Slot 4:  Empty slot'), 1)])\n"
	                      "d['key_green'].setText(_('Reboot'))\nd['key_yellow'].setText(_('Delete'))\nd['key_info'].setText(_('INFO'))"], [], 2),
	"kexecinit": ("from Screens.MultiBootManager import KexecInit\nsession.open(KexecInit)", [], 2),
	# Kullanim & Arayuz > "Setup - TiviAtv-FHD" (openATV'nin AtileHD eklentisi) ve TiviATV Settings
	"atilehd": ("from Plugins.Extensions.AtileHD.plugin import AtileHD_Config\nsession.open(AtileHD_Config)", [], 2),
	# AtileHD_Config'in "pro" acikken sari tusu ve mavi "About" tusu
	"atilehd-pro": ("from Plugins.Extensions.AtileHD.plugin import AtileHD_Config\nscr = session.open(AtileHD_Config)\n"
	                "scr.myAtileHD_active.value = True\nscr.createConfigList()", [], 2),
	"atilehd-about": (["from Plugins.Extensions.AtileHD.plugin import AtileHD_Config\nsession.open(AtileHD_Config)",
	                   "session.current_dialog.about()"], [], 1.5),
	"atilehd-screens": (["from Plugins.Extensions.AtileHD.plugin import AtileHD_Config\nsession.open(AtileHD_Config)",
	                     "from Plugins.Extensions.AtileHD.plugin import AtileHDScreens\nsession.open(AtileHDScreens)"], [], 1.5),
	# mavi tus: hizli menu; yazilim guncelleme (besleme yoksa durum "unavailable")
	"quickmenu": ("from Screens.QuickMenu import QuickMenu\nsession.open(QuickMenu)", [], 2),
	"softwareupdate": ("from Screens.SoftwareUpdate import SoftwareUpdate\nsession.open(SoftwareUpdate)", [], 4),
	# File Commander ve alt ekranlari
	"filecommander": ("from Plugins.Extensions.FileCommander.plugin import FileCommander\nsession.open(FileCommander, '/usr/share/enigma2/', '/etc/enigma2/')", ["Down", "Down", "Down", "Down", "Down", "Down", "Down", "Down", "Down", "Down"], 1.5),
	"filecommander-menu": (["from Plugins.Extensions.FileCommander.plugin import FileCommander\nsession.open(FileCommander, '/usr/share/enigma2/', '/etc/enigma2/')",
	                        "session.current_dialog.keyMenu()"], [], 1.5),
	"filecommander-data": (["from Plugins.Extensions.FileCommander.plugin import FileCommander\nsession.open(FileCommander, '/usr/share/enigma2/', '/etc/enigma2/')",
	                        "from Plugins.Extensions.FileCommander.plugin import FileCommanderData\nsession.open(FileCommanderData, {'Title': 'Information', 'Data': ['Name:\\tskin.xml', 'Size:\\t212 KB', 'Owner:\\troot', 'Modified:\\t13.10.2026 02:14']})"], [], 1.5),
	"filecommander-viewer": (["from Plugins.Extensions.FileCommander.plugin import FileCommander\nsession.open(FileCommander, '/usr/share/enigma2/', '/etc/enigma2/')",
	                          "from Plugins.Extensions.FileCommander.plugin import FileCommanderFileViewer\nsession.open(FileCommanderFileViewer, '/etc/enigma2/settings', isText=True)"], [], 1.5),
	"filecommander-editor": (["from Plugins.Extensions.FileCommander.plugin import FileCommander\nsession.open(FileCommander, '/usr/share/enigma2/', '/etc/enigma2/')",
	                          "from Plugins.Extensions.FileCommander.plugin import FileCommanderTextEditor\nsession.open(FileCommanderTextEditor, '/etc/enigma2/settings')"], [], 1.5),
	# eklentiler: Media Player, Picture Player, Programmlisten-Updater, gecmis zaplama
	"mediaplayer": ("from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer\nsession.open(MediaPlayer)", [], 2.5),
	"picshow": ("from Plugins.Extensions.PicturePlayer.ui import picshow\nfrom Components.config import config\n"
	            "config.pic.lastDir.value = '/home/user/tiviatv-fhd/docs/screenshots/'\nsession.open(picshow)", [], 3),
	"pic-exif": ("from Plugins.Extensions.PicturePlayer.ui import Pic_Exif\n"
	             "session.open(Pic_Exif, ['/media/hdd/pictures/holiday-042.jpg', '0230', 'Canon', 'EOS R6', '2026:08:14 18:42:07', '6000/4000', 'No', 'Normal', '', 'Pattern', 'Manual', 'Daylight', '', '400', '300', '300', 'inch', '', '1/250', '0', '', '', 'f/4.0'])", [], 1.5),
	"programmlisten": ("from Plugins.Extensions.ProgrammlistenUpdater.plugin import PUMainScreen\nsession.open(PUMainScreen)", [], 4),
	"historyzap": ("from enigma import eServiceCenter\nfrom Screens.ChannelSelection import HistoryZapSelector\n"
	               "refs = eServiceCenter.getInstance().list(ib.servicelist.getRoot()).getContent('R', True)[:6]\n"
	               "session.open(HistoryZapSelector, refs, 0, 1)", [], 1.5),
	# Bluetooth ve hava durumu eklentileri emulatorde kurulu degil: ayni ekran
	# adi ve widget adlariyla benzetim (OAWeather'in kendi converter'i yok,
	# session.OAWeather'li widget'lar atlanir; duzen ve liste sablonu gorunur)
	"bluetooth": ("from Screens.Screen import Screen\nfrom Components.ActionMap import ActionMap\n"
	              "from Components.Sources.StaticText import StaticText\nfrom Components.Label import Label\nfrom Components.MenuList import MenuList\n"
	              "class BluetoothDevicesManager(Screen):\n"
	              "\tdef __init__(self, session):\n"
	              "\t\tScreen.__init__(self, session)\n"
	              "\t\tself.setTitle('Bluetooth Devices Manager')\n"
	              "\t\tfor k, t in (('red', 'Exit'), ('green', 'Scan'), ('yellow', 'Disconnect'), ('blue', 'Audio Off')): self['key_' + k] = StaticText(t)\n"
	              "\t\tself['devicelist'] = MenuList([('JBL Flip 5 / Connected / Audio', ''), ('Logitech K400 / Not connected', ''), ('Xbox Wireless Controller / Not connected', '')])\n"
	              "\t\tself['ConnStatus'] = Label('Connection with:\\nJBL Flip 5')\n"
	              "\t\tself['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.close}, -1)\n"
	              "session.open(BluetoothDevicesManager)", [], 1.5),
	"bluetooth-vu": ("from Screens.Screen import Screen\nfrom Components.ActionMap import ActionMap\n"
	                 "from Components.Label import Label\nfrom Components.MenuList import MenuList\n"
	                 "class BluetoothDevicesManager(Screen):\n"
	                 "\tdef __init__(self, session):\n"
	                 "\t\tScreen.__init__(self, session)\n"
	                 "\t\tself.setTitle('Bluetooth Setup')\n"
	                 "\t\tfor k, t in (('red', 'Exit'), ('green', ' '), ('yellow', 'Connect'), ('blue', 'Scan')): self['key_' + k] = Label(t)\n"
	                 "\t\tself['devicelist'] = MenuList([('Vu+ Bluetooth RCU / Not connected', '')])\n"
	                 "\t\tself['ConnStatus'] = Label('Not connected to any device')\n"
	                 "\t\tself['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.close}, -1)\n"
	                 "session.open(BluetoothDevicesManager)", [], 1.5),
	"msnweather": ("from Screens.Screen import Screen\nfrom Components.ActionMap import ActionMap\n"
	               "from Components.Sources.StaticText import StaticText\nfrom Components.Pixmap import Pixmap\n"
	               "class MSNWeatherPlugin(Screen):\n"
	               "\tdef __init__(self, session):\n"
	               "\t\tScreen.__init__(self, session)\n"
	               "\t\tself.setTitle('Weather Plugin')\n"
	               "\t\tfor k, t in (('caption', 'Istanbul, TR'), ('currentTemp', '18°C'), ('condition', 'Partly cloudy'), ('wind_condition', 'Wind: 14 km/h NE'),\n"
	               "\t\t             ('humidity', 'Humidity: 64 %'), ('observationtime', 'Observation time: 14:20'), ('observationpoint', 'Observation point: Istanbul'),\n"
	               "\t\t             ('feelsliketemp', 'Feels like 17°C'), ('statustext', '')): self[k] = StaticText(t)\n"
	               "\t\tdays = (('Tue', '14. Oct', 19, 12, 'Sunny'), ('Wed', '15. Oct', 17, 11, 'Showers'), ('Thu', '16. Oct', 16, 10, 'Rain'), ('Fri', '17. Oct', 18, 11, 'Cloudy'), ('Sat', '18. Oct', 20, 12, 'Sunny'))\n"
	               "\t\tfor i, (d, dt, hi, lo, tx) in enumerate(days):\n"
	               "\t\t\tself['weekday%d' % (i + 1)] = StaticText('%s\\n%s' % (d, dt))\n"
	               "\t\t\tself['weekday%d_temp' % (i + 1)] = StaticText('%d°C|%d°C\\n%s' % (hi, lo, tx))\n"
	               "\t\t\tself['weekday%d_icon' % (i + 1)] = Pixmap()\n"
	               "\t\tself['currenticon'] = Pixmap()\n"
	               "\t\tself['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.close}, -1)\n"
	               "session.open(MSNWeatherPlugin)", [], 1.5),
	"oaweather-favorites": ("from Screens.Screen import Screen\nfrom Components.ActionMap import ActionMap\n"
	                        "from Components.Sources.StaticText import StaticText\nfrom Components.Sources.List import List\n"
	                        "class OAWeatherFavorites(Screen):\n"
	                        "\tdef __init__(self, session):\n"
	                        "\t\tScreen.__init__(self, session)\n"
	                        "\t\tself.setTitle('Weather Favorites')\n"
	                        "\t\tself['headline'] = StaticText('Manage your favorites')\n"
	                        "\t\tfor k, t in (('red', 'Delete'), ('green', 'Save'), ('yellow', 'Edit'), ('blue', 'Add')): self['key_' + k] = StaticText(t)\n"
	                        "\t\tself['favoriteList'] = List([('Istanbul, TR', '[lon=28.97835, lat=41.08218]'), ('Ankara, TR', '[lon=32.85427, lat=39.91987]'), ('Hamburg, DE', '[lon=10.00065, lat=53.55034]')])\n"
	                        "\t\tself['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.close}, -1)\n"
	                        "session.open(OAWeatherFavorites)", [], 1.5),
	"oaweather-detail": ("from Screens.Screen import Screen\nfrom Components.ActionMap import ActionMap\n"
	                      "from Components.Sources.StaticText import StaticText\nfrom Components.Sources.List import List\n"
	                      "from Components.Label import Label\nfrom Components.Pixmap import Pixmap\n"
	                      "class OAWeatherDetailview(Screen):\n"
	                      "\tdef __init__(self, session):\n"
	                      "\t\tScreen.__init__(self, session)\n"
	                      "\t\tself.setTitle('Weather Plugin Detailview')\n"
	                      "\t\tfor k, t in (('red', 'Exit'), ('green', 'Chose favorite'), ('yellow', 'Previous favorite'), ('blue', 'Next favorite'), ('channel', 'Day +/-'), ('info', 'Details +/-'), ('ok', 'Glass')): self['key_' + k] = StaticText(t)\n"
	                      "\t\tfor k, t in (('sunrise', '07:21'), ('sunset', '18:34'), ('moonrise', '22:10'), ('moonset', '13:02'), ('version', ''), ('statustext', '')): self[k] = StaticText(t)\n"
	                      "\t\tself['update'] = Label('Update')\n\t\tself['currdatetime'] = Label('Today 13 Oct')\n"
	                      "\t\tself['moonrisepix'] = Pixmap()\n\t\tself['moonsetpix'] = Pixmap()\n"
	                      "\t\trows = []\n"
	                      "\t\tfor h, t, f, hu, pr, ws, wd, g, uv, ps, vi, sd in (('14:00 h', '18 °C', '17 °C', '64 %', '10 %', '14 km/h', 'NE', '28 km/h', '3', '1016 mbar', '24 km', 'Partly cloudy'),\n"
	                      "\t\t        ('15:00 h', '18 °C', '17 °C', '62 %', '10 %', '15 km/h', 'NE', '30 km/h', '2', '1016 mbar', '24 km', 'Partly cloudy'),\n"
	                      "\t\t        ('16:00 h', '17 °C', '16 °C', '66 %', '20 %', '13 km/h', 'E', '26 km/h', '1', '1015 mbar', '20 km', 'Cloudy'),\n"
	                      "\t\t        ('17:00 h', '16 °C', '15 °C', '70 %', '40 %', '12 km/h', 'E', '24 km/h', '0', '1015 mbar', '16 km', 'Light rain showers'),\n"
	                      "\t\t        ('18:00 h', '15 °C', '14 °C', '75 %', '60 %', '11 km/h', 'SE', '22 km/h', '0', '1014 mbar', '12 km', 'Rain'),\n"
	                      "\t\t        ('19:00 h', '14 °C', '13 °C', '78 %', '50 %', '10 km/h', 'SE', '20 km/h', '0', '1014 mbar', '12 km', 'Rain'),\n"
	                      "\t\t        ('20:00 h', '14 °C', '13 °C', '80 %', '30 %', '9 km/h', 'S', '18 km/h', '0', '1014 mbar', '14 km', 'Cloudy')):\n"
	                      "\t\t\trows.append((h, ps, t, f, hu, pr, ws, wd, g, uv, vi, sd, sd, None) + (None,) * 10)\n"
	                      "\t\tself['detailList'] = List(rows)\n"
	                      "\t\tself['actions'] = ActionMap(['OkCancelActions', 'InfoActions'], {'cancel': self.close, 'info': self.toggle}, -1)\n"
	                      "\t\tself.onLayoutFinish.append(self.first)\n"
	                      "\tdef first(self):\n"
	                      "\t\tself['detailList'].setStyle('default')\n"
	                      "\tdef toggle(self):\n"
	                      "\t\tself['detailList'].setStyle('reduced' if self['detailList'].style == 'default' else 'default')\n"
	                      "session.open(OAWeatherDetailview)", [], 1.5),
	"oaweather-frame": ("from Screens.Screen import Screen\nfrom Components.ActionMap import ActionMap\n"
	                    "from Components.Sources.StaticText import StaticText\nfrom Components.Pixmap import Pixmap\n"
	                    "class OAWeatherDetailFrame(Screen):\n"
	                    "\tdef __init__(self, session):\n"
	                    "\t\tScreen.__init__(self, session)\n"
	                    "\t\tvals = ('15:00 h', '1016 mbar', '18 °C', '17 °C', '62 %', '10 %', '15 km/h', 'NE', '30 km/h', '2', '24 km', 'Partly cloudy', 'Clouds come and go, a light breeze from the north-east. It stays dry until the evening.')\n"
	                    "\t\tfor k, v in zip(('time', 'pressure', 'temp', 'feels', 'humid', 'precip', 'windspeed', 'winddir', 'windgusts', 'uvindex', 'visibility', 'shortdesc', 'longdesc'), vals): self[k] = StaticText(v)\n"
	                    "\t\tself['icon'] = Pixmap()\n"
	                    "\t\tself['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.close}, -1)\n"
	                    "session.open(OAWeatherDetailFrame)", [], 1.5),
	"oaweather-overview": ("from Screens.Screen import Screen\nfrom Components.ActionMap import ActionMap\n"
	                       "from Components.Sources.StaticText import StaticText\nfrom Components.Label import Label\n"
	                       "class OAWeatherOverview(Screen):\n"
	                       "\tdef __init__(self, session):\n"
	                       "\t\tScreen.__init__(self, session)\n"
	                       "\t\tself.setTitle('Weather Plugin Overview')\n"
	                       "\t\tfor k, t in (('red', 'Exit'), ('green', 'Chose favorite'), ('yellow', 'Previous favorite'), ('blue', 'Next favorite'), ('ok', 'View details'), ('menu', 'Settings')): self['key_' + k] = StaticText(t)\n"
	                       "\t\tself['update'] = Label('Update')\n\t\tself['current'] = Label('Current Weather')\n"
	                       "\t\tself['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.close}, -1)\n"
	                       "session.open(OAWeatherOverview)", [], 1.5),
	# FileList parametreleri skinlenmemis dizin secicide de gecerli
	"locationbox": ("from Screens.LocationBox import LocationBox\nsession.open(LocationBox, text='Choose a directory', currDir='/usr/share/enigma2/')", [], 2),
	# mavi tus > Softcam > Softcam Settings (emulatorde /etc/init.d/softcam.* ornek betikleri ve /tmp/ecm.info gerekir)
	"softcamsetup": ("from Screens.SoftcamSetup import SoftcamSetup\nsession.open(SoftcamSetup)", [], 2),
	"tiviatvsettings": ("from Plugins.Extensions.TiviAtvFont.plugin import TiviAtvSettings\nsession.open(TiviAtvSettings)", [], 2),
	# Kurulum > Kullanim & Arayuz altindaki ayar ekranlari
	"buttonsetup": ("from Screens.ButtonSetup import ButtonSetup\nsession.open(ButtonSetup)", [], 1.5),
	"buttonsetupselect": (["from Screens.ButtonSetup import ButtonSetup\nsession.open(ButtonSetup)",
	                       "from Screens.ButtonSetup import ButtonSetupSelect\n"
	                       "session.open(ButtonSetupSelect, session.current_dialog['list'].getCurrent())"], [], 1.5),
	# emulatorde giris aygiti yok: goruntu icin listeye kutudakine benzer ornek satirlar konur
	"inputdevices": (["from Screens.InputDeviceSetup import InputDeviceSelection\nsession.open(InputDeviceSelection)",
	                  "from Tools.LoadPixmap import LoadPixmap\nfrom Tools.Directories import resolveFilename, SCOPE_GUISKIN\n"
	                  "px = lambda n: LoadPixmap(resolveFilename(SCOPE_GUISKIN, 'icons/%s.png' % n))\n"
	                  "session.current_dialog['list'].setList([('event0', 'Advanced remote control', px('input_rcnew-configured'), None), "
	                  "('event1', 'Front panel buttons', px('input_rcnew'), None), ('event2', 'USB keyboard', px('input_keyboard'), None)])"], [], 1.5),
	"localeselection": ("from Screens.LocaleSelection import LocaleSelection\nsession.open(LocaleSelection)", [], 2),
	"helpmenu": ("ib.showHelp() if hasattr(ib, 'showHelp') else None", [], 1.5),
}

# session.close ertelenmis calisir (delay_timer): her cagrida tek ekran kapanir
CLOSE_ONE = IB + """
cur = session.current_dialog
if cur is ib:
	out("IB")
elif cur is ib.servicelist:
	ib.servicelist.cancel()  # kanal listesi kapanmaz, gizlenir
else:
	cur.close()
"""
CLEANUP = IB + """
if ib.secondInfoBarScreen: ib.secondInfoBarScreen.hide()
from Components.VolumeControl import VolumeControl
v = VolumeControl.instance
if v.volctrl.isMuted(): v.volMute()  # once sesi ac: volMute ses cubugunu yeniden gosterir
v.volumeDialog.hide(); v.muteDialog.hide()
ib.hide()
"""


def close_all():
	for _ in range(10):
		if "IB" in run(CLOSE_ONE):
			break
		time.sleep(0.4)
	run(CLEANUP)


def run(code):
	return subprocess.run(["e2-py", code], capture_output=True, text=True).stdout


def main():
	OUT.mkdir(parents=True, exist_ok=True)
	for name, (code, keys, wait) in SCREENS.items():
		if ONLY and name not in ONLY:
			continue
		close_all()
		time.sleep(0.5)  # InfoBar'in gizlenmesi bitsin
		for step in [code] if isinstance(code, str) else code:
			res = run(IB + step)
			if not res.startswith("OK"):
				break
			time.sleep(0.8)
		if not res.startswith("OK"):
			print("%-20s ACILAMADI\n%s" % (name, res.strip().splitlines()[-1] if res.strip() else "cevap yok"))
			continue
		if keys:
			time.sleep(1)
			subprocess.run(["e2-tus", "-b", "0.8"] + keys)
		time.sleep(wait)
		cur = run("out(session.current_dialog.__class__.__name__, getattr(session.current_dialog, 'skinName', ''))").splitlines()
		subprocess.run(["e2-ekran", name, str(OUT)] + KARE, capture_output=True)
		print("%-20s %s" % (name, cur[1] if len(cur) > 1 else "?"))
	close_all()


if __name__ == "__main__":
	main()
