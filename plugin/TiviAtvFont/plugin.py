# TiviATV FHD  -  yazi tipi secici ve skin ayarlari
#
# Skin klasorundeki ve /usr/share/fonts altindaki yazi tiplerini listeler,
# secileni TiviAtv-FHD/fonts.xml'e yazar. skin.xml bu dosyayi <include> ile
# yukledigi icin skin.xml'e hic dokunulmaz; font adlari (TM/TMM/TMB/TMX)
# her zaman ayni kalir.
#
# Secim listesi enigma2'nin ChoiceBox ekranidir; gorunumu tamamen skin.xml'deki
# <screen name="ChoiceBox"> tanimindan gelir - eklentinin icinde gomulu skin yok.
#
# "TiviATV Settings": kanal listesinin EPG paneli (siradaki programlar,
# primetime) ve uzun aciklamalarin kaymasi. Ayarlar config.plugins.TiviAtv'de;
# tanimlari TiviAtvEpg converter'inda, skin onlari aninda uygular.
#
# Kurulum: /usr/lib/enigma2/python/Plugins/Extensions/TiviAtvFont/

from os import listdir, path

from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.BoundFunction import boundFunction

SKIN_DIR = "/usr/share/enigma2/TiviAtv-FHD"
FONTS_XML = path.join(SKIN_DIR, "fonts.xml")
FONT_DIRS = (SKIN_DIR, "/usr/share/fonts")

# skin.xml'in bekledigi dort ad ve her biri icin agirlik tercih sirasi
SLOTS = (
	("TM", ("Regular", "Book", "Light", "Medium", "SemiBold", "Bold")),
	("TMM", ("Medium", "Regular", "SemiBold", "Book", "Bold")),
	("TMB", ("SemiBold", "DemiBold", "Bold", "Medium", "Regular")),
	("TMX", ("Bold", "Black", "Heavy", "SemiBold", "Medium", "Regular")),
)
WEIGHTS = ("Thin", "Light", "Book", "Regular", "Medium", "SemiBold", "DemiBold", "Bold", "Black", "Heavy")

# Ayni piksel boyunda aileler farkli buyuklukte gorunur; skin olculeri dar bir
# font (Sony Sketch) icin kuruldu. Genis / iri x-yukseklikli aileler kucultulur ki
# yazilar kutularina sigsin. Listede olmayan aile 100.
SCALE = {"Inter": 92, "Geist": 94}

TEMPLATE = """<skin>
\t<!-- TiviATV FHD  -  active typeface set
\t     Written by the "TiviATV Font" plugin; can also be edited by hand.
\t     skin.xml loads it with <include>; the font names never change. -->
\t<fonts>
%s
\t\t<!-- font that comes with the box (VFD and fallback) -->
\t\t<font filename="nmsbd.ttf"  name="Regular" scale="100" />
\t\t<!-- aliases enigma2 expects -->
\t\t<alias name="Body"       font="TM"  size="30" height="40" />
\t\t<alias name="TextNormal" font="TM"  size="30" height="40" />
\t\t<alias name="ChoiceList" font="TM"  size="30" height="60" />
\t\t<alias name="VirtualKeyboard" font="TM" size="34" height="76" />
\t\t<alias name="PluginBrowser0" font="TM" size="30" height="75" />
\t\t<alias name="PluginBrowser1" font="TM" size="22" height="28" />
\t</fonts>
</skin>
"""


# Metinler Ingilizce; kutunun arayuz dili Turkceyse Turkcesi gosterilir
# (skin.xml'deki yazilar da enigma2'nin cevirisiyle ayni sekilde Turkcelesir).
TURKISH = {
	"TiviATV Font": "TiviATV Yazı Tipi",
	"Choose the skin typeface": "Skin yazı tipini seç",
	"Could not write fonts.xml: %s": "fonts.xml yazılamadı: %s",
	"Typeface: %s": "Yazı tipi: %s",
	"Restart the GUI now?": "Arayüz şimdi yeniden başlatılsın mı?",
	"No fonts found.": "Yazı tipi bulunamadı.",
	"GUI typeface": "Arayüz yazı tipi",
	"%d weights": "%d ağırlık",
	"active": "etkin",
	"TiviATV Settings": "TiviATV Ayarları",
	"Channel list and description options": "Kanal listesi ve açıklama seçenekleri",
	"Channel list: upcoming programmes": "Kanal listesi: sıradaki programlar",
	"Primetime": "Primetime",
	"Scroll long descriptions": "Uzun açıklamaları kaydır",
	"Shows the 5 programmes after NOW and NEXT of the selected channel above the programme card.": "Seçili kanalın NOW ve NEXT'ten sonraki 5 programını program kartının üstünde gösterir.",
	"Adds the programme at this time (today, or tomorrow once it is over) to the list.": "Bu saatteki programı (bugün; bittiyse yarın) listeye ekler.",
	"Descriptions that do not fit slowly scroll up, then start again.": "Sığmayan açıklamalar yavaşça yukarı kayar, sonra baştan başlar.",
	"Cancel": "İptal",
	"Save": "Kaydet",
}


def turkish():
	"""Arayuz dili Turkce mi: openATV 7+ International, eskisinde Language."""
	try:
		from Components.International import international
		return international.getLocale().lower().startswith("tr")
	except Exception:
		pass
	try:
		from Components.Language import language
		return language.getLanguage().lower().startswith("tr")
	except Exception:
		return False


def tr(text):
	return TURKISH.get(text, text) if turkish() else _(text)


def splitWeight(base):
	"""'Barlow-SemiBold' -> ('Barlow', 'SemiBold'); taninmayan sonek ailenin parcasidir."""
	for sep in ("-", "_"):
		head, found, tail = base.rpartition(sep)
		if found and tail in WEIGHTS:
			return head, tail
	return base, ""


def scanFamilies():
	"""{aile: {agirlik: dosya adi}}"""
	families = {}
	for directory in FONT_DIRS:
		if not path.isdir(directory):
			continue
		for filename in sorted(listdir(directory)):
			if not filename.lower().endswith((".ttf", ".otf")):
				continue
			if "italic" in filename.lower():  # arayuz icin italik varyantlar gereksiz
				continue
			if "icons" in filename.lower():  # enigma2icons gibi glif fontlari harf icermez
				continue
			family, weight = splitWeight(filename.rsplit(".", 1)[0])
			families.setdefault(family, {}).setdefault(weight, filename)
	return families


def fontsBlock(family, weights):
	"""Dort slotu ailenin mevcut agirliklarindan doldurur."""
	lines = []
	for name, order in SLOTS:
		filename = None
		for weight in order:
			if weight in weights:
				filename = weights[weight]
				break
		if filename is None:  # tek agirlikli aile
			filename = sorted(weights.values())[0]
		lines.append('\t\t<font filename="%s" name="%s" scale="%d" />' % (filename, name, SCALE.get(family, 100)))
	return "\t\t<!-- %s -->\n%s" % (family, "\n".join(lines))


def currentFamily(families):
	"""fonts.xml'de TM hangi dosyaya bakiyorsa aktif aile odur."""
	try:
		with open(FONTS_XML) as handle:
			lines = handle.read().splitlines()
	except OSError:
		return None
	for line in lines:
		if 'name="TM"' not in line:
			continue
		for family, weights in families.items():
			for filename in weights.values():
				if 'filename="%s"' % filename in line:
					return family
	return None


def chosen(session, families, answer):
	if not answer:
		return
	family = answer[1]
	try:
		with open(FONTS_XML, "w") as handle:
			handle.write(TEMPLATE % fontsBlock(family, families[family]))
	except OSError as err:
		session.open(MessageBox, tr("Could not write fonts.xml: %s") % err, MessageBox.TYPE_ERROR, timeout=8)
		return
	session.openWithCallback(
		boundFunction(restartAsked, session), MessageBox,
		(tr("Typeface: %s") % family) + "\n\n" + tr("Restart the GUI now?"),
		MessageBox.TYPE_YESNO)


def restartAsked(session, answer):
	if answer:
		session.open(TryQuitMainloop, 3)  # 3 = arayuzu yeniden baslat


def main(session, **kwargs):
	families = scanFamilies()
	if not families:
		session.open(MessageBox, tr("No fonts found."), MessageBox.TYPE_ERROR, timeout=5)
		return
	names = sorted(families.keys(), key=str.lower)
	current = currentFamily(families)
	entries = []
	for name in names:
		count = len(families[name])
		label = name if count == 1 else "%s   (%s)" % (name, tr("%d weights") % count)
		if name == current:
			label = label + "   -  " + tr("active")
		entries.append((label, name))
	session.openWithCallback(
		boundFunction(chosen, session, families), ChoiceBox,
		title=tr("GUI typeface"), list=entries,
		selection=names.index(current) if current in names else 0)


class TiviAtvSettings(ConfigListScreen, Screen):
	"""Gorunumu skin.xml'deki <screen name="TiviAtvSettings">; yoksa Setup."""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["TiviAtvSettings", "Setup"]
		self.setTitle(tr("TiviATV Settings"))
		from Components.Converter.TiviAtvEpg import settings
		options = settings()
		self.help = {}
		entries = []
		for label, item, text in (
			("Channel list: upcoming programmes", options.epgPanel, "Shows the 5 programmes after NOW and NEXT of the selected channel above the programme card."),
			("Primetime", options.primetime, "Adds the programme at this time (today, or tomorrow once it is over) to the list."),
			("Scroll long descriptions", options.scroll, "Descriptions that do not fit slowly scroll up, then start again."),
		):
			entries.append(getConfigListEntry(tr(label), item))
			self.help[tr(label)] = tr(text)
		self["description"] = Label()
		self["key_red"] = StaticText(tr("Cancel"))
		self["key_green"] = StaticText(tr("Save"))
		ConfigListScreen.__init__(self, entries, session=session)
		self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"save": self.keySave,
			"green": self.keySave,
			"ok": self.keySave,
		}, -2)
		self["config"].onSelectionChanged.append(self.describe)
		self.onLayoutFinish.append(self.describe)

	def describe(self):
		current = self["config"].getCurrent()
		self["description"].setText(self.help.get(current[0], "") if current else "")


def settingsMain(session, **kwargs):
	session.open(TiviAtvSettings)


def menuHook(menuid, **kwargs):
	# menu.xml: "Usage & GUI" menusunun key'i "system"
	if menuid == "system":
		return [(tr("TiviATV Font"), main, "tiviatv_font", 10),
		        (tr("TiviATV Settings"), settingsMain, "tiviatv_settings", 11)]
	return []


def Plugins(**kwargs):
	return [
		PluginDescriptor(name=tr("TiviATV Font"), description=tr("Choose the skin typeface"),
		                 where=PluginDescriptor.WHERE_PLUGINMENU, icon=None, fnc=main),
		PluginDescriptor(name=tr("TiviATV Settings"), description=tr("Channel list and description options"),
		                 where=PluginDescriptor.WHERE_PLUGINMENU, icon=None, fnc=settingsMain),
		PluginDescriptor(name=tr("TiviATV Font"), description=tr("Choose the skin typeface"),
		                 where=PluginDescriptor.WHERE_MENU, fnc=menuHook),
	]
