# TiviATV FHD  -  yazi tipi secici
#
# Skin klasorundeki ve /usr/share/fonts altindaki yazi tiplerini listeler,
# secileni TiviAtv-FHD/fonts.xml'e yazar. skin.xml bu dosyayi <include> ile
# yukledigi icin skin.xml'e hic dokunulmaz; font adlari (TM/TMM/TMB/TMX)
# her zaman ayni kalir.
#
# Secim listesi enigma2'nin ChoiceBox ekranidir; gorunumu tamamen skin.xml'deki
# <screen name="ChoiceBox"> tanimindan gelir - eklentinin icinde gomulu skin yok.
#
# Kurulum: /usr/lib/enigma2/python/Plugins/Extensions/TiviAtvFont/

from os import listdir, path

from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
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

TEMPLATE = """<skin>
\t<!-- TiviATV FHD  -  aktif yazi tipi seti
\t     Bu dosyayi "TiviATV Yazi Tipi" eklentisi uretir; elle de duzenlenebilir.
\t     skin.xml bunu <include> ile yukler, font adlari hep ayni kalir. -->
\t<fonts>
%s
\t\t<!-- kutuda hazir gelen fontlar (VFD ve yedek icin) -->
\t\t<font filename="nmsbd.ttf"  name="Regular" scale="100" />
\t\t<!-- enigma2'nin bekledigi takma adlar -->
\t\t<alias name="Body"       font="TM"  size="30" height="40" />
\t\t<alias name="TextNormal" font="TM"  size="30" height="40" />
\t\t<alias name="ChoiceList" font="TM"  size="30" height="48" />
\t</fonts>
</skin>
"""


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
		lines.append('\t\t<font filename="%s" name="%s" scale="100" />' % (filename, name))
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
		session.open(MessageBox, _("fonts.xml yazilamadi: %s") % err, MessageBox.TYPE_ERROR, timeout=8)
		return
	session.openWithCallback(
		boundFunction(restartAsked, session), MessageBox,
		(_("Yazi tipi: %s") % family) + "\n\n" + _("Arayuz simdi yeniden baslatilsin mi?"),
		MessageBox.TYPE_YESNO)


def restartAsked(session, answer):
	if answer:
		session.open(TryQuitMainloop, 3)  # 3 = arayuzu yeniden baslat


def main(session, **kwargs):
	families = scanFamilies()
	if not families:
		session.open(MessageBox, _("Yazi tipi bulunamadi."), MessageBox.TYPE_ERROR, timeout=5)
		return
	names = sorted(families.keys(), key=str.lower)
	current = currentFamily(families)
	entries = []
	for name in names:
		count = len(families[name])
		label = name if count == 1 else "%s   (%d agirlik)" % (name, count)
		if name == current:
			label = label + "   -  etkin"
		entries.append((label, name))
	session.openWithCallback(
		boundFunction(chosen, session, families), ChoiceBox,
		title=_("Arayuz yazi tipi"), list=entries,
		selection=names.index(current) if current in names else 0)


def menuHook(menuid, **kwargs):
	# menu.xml: "Usage & GUI" menusunun key'i "system"
	if menuid == "system":
		return [(_("TiviATV Yazi Tipi"), main, "tiviatv_font", 10)]
	return []


def Plugins(**kwargs):
	return [
		PluginDescriptor(name=_("TiviATV Yazi Tipi"), description=_("Skin yazi tipini sec"),
		                 where=PluginDescriptor.WHERE_PLUGINMENU, icon=None, fnc=main),
		PluginDescriptor(name=_("TiviATV Yazi Tipi"), description=_("Skin yazi tipini sec"),
		                 where=PluginDescriptor.WHERE_MENU, fnc=menuHook),
	]
