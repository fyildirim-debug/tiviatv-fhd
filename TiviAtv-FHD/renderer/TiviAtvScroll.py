# TiviATV FHD  -  kutusuna sigmayan metni yavasca yukari kaydiran Label
#
#   <widget source="ServiceEvent" render="TiviAtvScroll" position=... size=... font=... >
#       <convert type="EventName">FullDescription</convert>
#   </widget>
#
# Label gibi kullanilir. Metin sigiyorsa durur; sigmiyorsa 4 sn bekler, sonuna
# kadar kayar, 4 sn bekler, basa doner. Ekran gizliyken zamanlayici durur.
# "TiviATV Settings" eklentisinden kapatilabilir (config.plugins.TiviAtv.scroll):
# kapaliyken duz Label gibi ilk satirlari gosterir.
#
# Kurulum: /usr/lib/enigma2/python/Components/Renderer/TiviAtvScroll.py

from enigma import eLabel, ePoint, eSize, eTimer, eWidget

from Components.Renderer.Renderer import Renderer

TICK = 50  # ms; her adimda 1 piksel (20 px/sn, ~1 satir/1.5 sn)
PAUSE = 80  # adim: 4 sn

# kapsayicinin kendisinde kalanlar; digerleri (yazi tipi, renk, hiza) ic etikete
OWN = ("position", "size", "zPosition", "transparent", "backgroundColor", "cornerRadius")


def scrollEnabled():
	try:
		from Components.Converter.TiviAtvEpg import settings
		return bool(settings().scroll.value)
	except Exception:
		return True


class TiviAtvScroll(Renderer):
	GUI_WIDGET = eWidget

	def __init__(self):
		Renderer.__init__(self)
		self.label = None
		self.timer = eTimer()
		self.timer.callback.append(self.step)
		self.offset = self.overflow = self.wait = 0

	def postWidgetCreate(self, instance):
		self.label = eLabel(instance)

	def applySkin(self, desktop, parent):
		from skin import applyAllAttributes
		own = [(k, v) for k, v in self.skinAttributes if k in OWN]
		inner = [(k, v) for k, v in self.skinAttributes if k not in OWN or k in ("transparent", "backgroundColor")]
		self.skinAttributes = own
		result = Renderer.applySkin(self, desktop, parent)
		applyAllAttributes(self.label, desktop, inner, getattr(parent, "scale", ((1, 1), (1, 1))))
		self.changed((self.CHANGED_DEFAULT,))  # kaynak, etiket yokken baglanmisti
		return result

	def changed(self, what):
		if self.label is None:
			return
		text = getattr(self.source, "text", "") if self.source is not None and what[0] != self.CHANGED_CLEAR else ""
		self.label.setText(text or "")
		self.layout()

	def layout(self):
		self.timer.stop()
		if self.label is None or self.instance is None:
			return
		size = self.instance.size()
		width, height = size.width(), size.height()
		self.label.resize(eSize(width, height))
		textHeight = self.label.calculateSize().height()
		self.overflow = textHeight - height
		self.offset = 0
		self.label.move(ePoint(0, 0))
		if self.overflow > 0:
			self.label.resize(eSize(width, textHeight))
			if scrollEnabled() and not self.suspended:
				self.wait = PAUSE
				self.timer.start(TICK)

	def step(self):
		if self.wait > 0:
			self.wait -= 1
			if self.wait == 0 and self.offset >= self.overflow:  # sonda beklendi: basa don
				self.offset = 0
				self.label.move(ePoint(0, 0))
				self.wait = PAUSE
			return
		self.offset += 1
		self.label.move(ePoint(0, -self.offset))
		if self.offset >= self.overflow:
			self.wait = PAUSE

	def onShow(self):
		Renderer.onShow(self)
		self.layout()

	def onHide(self):
		Renderer.onHide(self)
		self.timer.stop()

	def destroy(self):
		self.timer.stop()
		self.timer.callback.remove(self.step)
		self.label = None
		Renderer.destroy(self)
