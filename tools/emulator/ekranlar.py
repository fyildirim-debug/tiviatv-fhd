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
	               "session.open(MessageBox, 'Kanal listesi kaydedilsin mi?\\nDegisiklikler kutuya yazilacak.', MessageBox.TYPE_YESNO)", [], 1.5),
	"choicebox": ("from Screens.ChoiceBox import ChoiceBox\n"
	              "session.open(ChoiceBox, title='Yazi tipi secin', list=[(n, n) for n in ('Barlow', 'Sony Sketch EF', 'DejaVu Sans', 'Liberation Sans', 'Roboto')])", [], 1.5),
	"audioselection": ("ib.audioSelection()", [], 2),
	"volume": ("from Components.VolumeControl import VolumeControl\nVolumeControl.instance.volUp()", [], 0.8),
	"mute": ("from Components.VolumeControl import VolumeControl\nVolumeControl.instance.volMute()", [], 0.8),
	# InfoBar.keyNumberGlobal oynatilan akis sarilabiliyorsa sarar; ekran dogrudan acilir
	"numberzap": ("from Screens.InfoBarGenerics import NumberZap\nfrom Components.config import config\nconfig.usage.numzappicon.value = True\nsession.open(NumberZap, 7, ib.searchNumber)", [], 0.6),
	"pluginbrowser": ("from Screens.PluginBrowser import PluginBrowser\nsession.open(PluginBrowser)", [], 2),
	# skinde henuz olmayan, sik acilan ekranlar
	"inputbox": ("from Screens.InputBox import InputBox\nsession.open(InputBox, title='Kanal adini girin', text='Kanal D')", [], 1.5),
	"pininput": ("from Screens.InputBox import PinInput\nfrom Components.config import config\nsession.open(PinInput, pinList=[1234], triesEntry=config.ParentalControl.retries.servicepin, title='PIN kodunu girin', windowTitle='Ebeveyn kilidi')", [], 1.5),
	"virtualkeyboard": ("from Screens.VirtualKeyBoard import VirtualKeyBoard\nsession.open(VirtualKeyBoard, title='Ara', text='mavi liman')", [], 2),
	"timereditlist": ("from RecordTimer import RecordTimerEntry\nfrom ServiceReference import ServiceReference\n"
	                  "from time import time\nrt = session.nav.RecordTimer\n"
	                  "if not rt.timer_list:\n"
	                  "\tfor i, (ref, name) in enumerate((('1:0:1:100:1:1:1A40000:0:0:0:', 'Ana Haber Bulteni'), ('1:0:1:102:1:1:1A40000:0:0:0:', 'Gece Sinemasi: Son Tren'))):\n"
	                  "\t\tt = int(time()) + 3600 * (i + 1)\n"
	                  "\t\trt.record(RecordTimerEntry(ServiceReference(ref), t, t + 3000, name, 'Ornek zamanlayici', None))\n"
	                  "from Screens.TimerEdit import TimerEditList\nsession.open(TimerEditList)", [], 2),
	"console": ("from Screens.Console import Console\nsession.open(Console, title='Paket kuruluyor', cmdlist=['echo opkg update; echo Downloading feed...; echo Updated source; echo Paket kuruldu.'])", [], 3),
	"textbox": ("from Screens.TextBox import TextBox\nsession.open(TextBox, text=open('/etc/image-version').read() * 6, title='Imaj bilgisi', skinName='TextBox')", [], 1.5),
	# skinName verilmezse TextBox ['None', 'TextBox'] listesi kurar; openATV skin.py
	# bu listeyi loglarken (", ".join) coker ve ekran widget'siz kalir (upstream hatasi)
	"information": ("from Screens.Information import InformationDistribution\nsession.open(InformationDistribution)", [], 3),
	"movieselection": ("from Screens.MovieSelection import MovieSelection\nsession.open(MovieSelection)", [], 3),
	"movieplayer": (["from Screens.InfoBar import MoviePlayer\nfrom enigma import eServiceReference\n"
	                 "ref = eServiceReference(4097, 0, '/opt/tivitest/kanal.ts')\nref.setName('Gece Sinemasi: Son Tren')\n"
	                 "session.open(MoviePlayer, ref)",
	                 "session.current_dialog.pauseService()"], [], 3),  # durum ikonu: duraklat
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
v.volumeDialog.hide(); v.muteDialog.hide()
if v.volctrl.isMuted(): v.volMute()
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
