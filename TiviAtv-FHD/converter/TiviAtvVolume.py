# TiviATV FHD  -  ses / sessiz penceresinin yeri (TiviATV Settings > Volume bar)
#
# Converter degil, skin applet'inin cagirdigi yardimci. Volume ve Mute ekrani
# bir kez kurulur; yer her gosterimde ayara gore uygulanir, ayar degisince
# yeniden baslatma gerekmez:
#
#   <applet type="onLayoutFinish">
#   try:
#   	from Components.Converter.TiviAtvVolume import place
#   	place(self, "volume")
#   except Exception:
#   	pass
#   </applet>
#
#   bottom  bilgi cubugunun hemen ustu (skindeki yer)
#   top     ustte ortada
#   left    solda dikey; pencere ve icindeki her oge 90 derece cevrilir,
#           ses cubugu alttan yukari dolar
#
# Kurulum: /usr/lib/enigma2/python/Components/Converter/TiviAtvVolume.py

from enigma import ePoint, eSize, getDesktop

MARGIN = 40  # 1080p'de kenar boslugu


def position():
	try:
		from Components.Converter.TiviAtvEpg import settings
		return settings().volumePos.value
	except Exception:
		return "bottom"


def children(screen):
	"""Penceredeki tum gorsel ogeler: skin eLabel'leri ve adli widget'lar."""
	items = [w for w in getattr(screen, "additionalWidgets", []) if getattr(w, "instance", None)]
	for component in screen.values():
		if getattr(component, "instance", None) is not None and hasattr(component.instance, "move"):
			items.append(component)
	return items


def place(screen, kind):
	state = {"applied": None}
	window = screen.instance
	original = (window.position().x(), window.position().y(), window.size().width(), window.size().height())
	geometry = [(item, item.instance.position().x(), item.instance.position().y(), item.instance.size().width(), item.instance.size().height())
		for item in children(screen)]
	slider = screen.get("Volume") if kind == "volume" else None

	def apply():
		mode = position()
		if mode == state["applied"]:
			return
		state["applied"] = mode
		desktop = getDesktop(0).size()
		scale = desktop.width() / 1920.0
		x, y, w, h = original
		vertical = mode == "left" and kind == "volume"
		for item, cx, cy, cw, ch in geometry:  # bu pencerede 90 derece: (x, y, w, h) -> (y, W - x - w, h, w)
			if vertical:
				item.instance.move(ePoint(cy, w - cx - cw))
				item.instance.resize(eSize(ch, cw))
			else:
				item.instance.move(ePoint(cx, cy))
				item.instance.resize(eSize(cw, ch))
		if slider is not None and getattr(slider, "instance", None):
			slider.instance.setOrientation(1 if vertical else 0, 1 if vertical else 0)
		text = screen.get("VolumeText") if kind == "volume" else None
		if text is not None and getattr(text, "instance", None):
			text.instance.setHAlign(1 if vertical else 2)  # dikeyde ortada, yatayda sagda
		if vertical:
			w, h = h, w
		window.resize(eSize(w, h))
		margin = int(MARGIN * scale)
		if mode == "top":
			window.move(ePoint((desktop.width() - w) // 2, margin))
		elif mode == "left":
			window.move(ePoint(margin, (desktop.height() - h) // 2))
		else:
			window.move(ePoint(original[0], original[1]))

	screen.onShow.append(apply)
	apply()
