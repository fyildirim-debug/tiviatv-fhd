# TiviATV FHD

A TiviMate-style 1920×1080 skin for openATV / enigma2. Translucent panels over
the running picture, white selection pills, rounded corners, thin progress
lines and the Inter typeface — all drawn by the enigma2 engine itself, **without
a single PNG**.

![TiviATV FHD: channel list, TV guide, infobar, multi EPG](docs/screenshots/hero.jpg)

**Türkçe:** [README.tr.md](README.tr.md) · [Installation](#installation) · [Screenshots](#screenshots)

## Requirements

openATV **7.3+**. `cornerRadius`, gradients and `itemCornerRadiusSelected`
landed in the enigma2 engine with 7.3; branches 7.2 and older don't have them,
so the corners come out square.

**OpenViX:** developed and tested on openATV, but OpenViX images with a recent
engine (rounded corners) also load it. The parts where OpenViX's screens differ
from openATV — colour keys created as `Button`, the classic plugin list — have
their own variants in the skin (see [Other images](#other-images-openvix)).

## Installation

1. **Connect to the box** over telnet or SSH (`ssh root@<box-ip>`). The box IP
   is shown in its network settings.
2. **Install.** Paste:

   ```sh
   wget -qO- https://raw.githubusercontent.com/fyildirim-debug/tiviatv-fhd/main/installer.sh | sh
   ```

   The script downloads the latest package, verifies its sha256 and installs
   it with `opkg`.
3. **Select the skin.** **Menu → Setup → Usage & GUI → Skin Settings** →
   `TiviAtv-FHD`, press **GREEN**; the GUI restarts.
4. **Switch the channel list to the TiviMate layout.** **Menu → Setup → Usage &
   GUI → Channel Selection Settings**:
   - "Show two lines per entry" = **Yes**
   - "Number of rows" = **10**

   Row height comes from this number (list height ÷ rows), not from the skin;
   change it if rows look too tight or too loose.
5. **Typeface (optional).** **TiviATV Font** in the same menu: Inter
   (default), Geist, Barlow or any other font on the box.

**Update:** run the same command again. Your font choice is kept.

**Language:** the skin's labels (NOW, NEXT, LATER), screen titles and the
font picker are in English and follow the box's GUI language where enigma2 has
a translation — on a Turkish GUI NOW / NEXT show as ŞİMDİ / SONRA, and the
font picker and signal percentages are Turkish too.

**Remove:**

```sh
opkg remove enigma2-plugin-skins-tiviatv-fhd
```

**Offline / manual:** copy the `.ipk` from [`dist/`](dist/) to `/tmp` on the
box (FTP or SCP), then:

```sh
opkg install /tmp/enigma2-plugin-skins-tiviatv-fhd_*_all.ipk
```

**Without the package:** copy `TiviAtv-FHD/` to `/usr/share/enigma2/`,
`TiviAtv-FHD/converter/*.py` to the converter directory,
`TiviAtv-FHD/renderer/*.py` to the renderer directory and
`plugin/TiviAtvFont/` to the plugin directory. Without the converters the skin
still opens; only the signal, badge and softcam (ECM) fields stay empty.

### Package contents

`enigma2-plugin-skins-tiviatv-fhd` installs to four places:

| Path | Contents |
|---|---|
| `/usr/share/enigma2/TiviAtv-FHD/` | skin, `fonts.xml`, typefaces, licenses, preview |
| `/usr/lib/enigma2/python/Components/Converter/` | `TiviAtvSignal.py`, `TiviAtvText.py`, `TiviAtvEcm.py`, `TiviAtvEpg.py` |
| `/usr/lib/enigma2/python/Components/Renderer/` | `TiviAtvScroll.py` |
| `/usr/lib/enigma2/python/Plugins/Extensions/TiviAtvFont/` | **TiviATV Font** (typeface) and **TiviATV Settings** |

| Converter | What it does |
|---|---|
| `TiviAtvSignal.py` | Signal (SNR/AGC) or IPTV stream rate in the infobar and channel list |
| `TiviAtvText.py` | Hides the resolution / codec / crypto badges while they are empty (on IPTV the crypto badge used to show as an empty pill) |
| `TiviAtvEcm.py` | Softcam ECM info (OSCam, CCcam …) from `/tmp/ecm.info` in the infobar, only on encrypted channels — see [Softcam (ECM) info](#softcam-ecm-info) |
| `TiviAtvEpg.py` | The channel list's optional EPG panel: the next programmes of the selected channel and primetime — see [TiviATV Settings](#tiviatv-settings) |
| `TiviAtvScroll.py` (renderer) | A label that slowly scrolls text that doesn't fit (the channel list description) |

`fonts.xml` is the package's conffile: if you changed it, opkg keeps your copy
and the install script merges your four font lines into the new version's
template, so font definitions added in later versions are never missing.

## Screenshots

Captured in the PC emulator with a sample channel list, EPG and picons (see
[Testing in the emulator](#testing-in-the-emulator)). The emulator plays no
video, so the OSD is laid over a sample broadcast frame by its alpha, the way
the box hardware composites it (frame: Unsplash, Vienna Reyes).

### Infobar

A bottom band that fades from the picture into dark, a thin-edged logo tile,
number chip + channel, programme, remaining time and badges that hide while
empty. The progress line is a 4 px hairline between the start and end times:
the fill flows from muted slate to bright white, so its tip is always the
brightest point. Bottom right shows SNR/AGC percentages on a satellite channel
and the stream rate on IPTV — both share the same spot, whichever source is
active is shown.

![Infobar](docs/screenshots/infobar.jpg)

On an encrypted channel the bottom right of the next-programme row shows what
the softcam is decoding with: system and CAID, reader, protocol, hops and ECM
time (see [Softcam (ECM) info](#softcam-ecm-info)).

![Infobar with OSCam ECM info](docs/screenshots/infobar-ecm.jpg)

Second infobar (OK while the infobar is open): the full description and genre.

![Second infobar](docs/screenshots/second-infobar.jpg)

### Channel list

As in TiviMate, the picture keeps playing full screen behind it (no PiG box):
a two-line list with picons and progress in a translucent panel on the left;
the selected channel gets a grey focus (a white pill would swallow white
logos). Bottom right is the now/next card of the selected channel, top right
the clock.

![Channel list](docs/screenshots/channelselection.jpg)

With **TiviATV Settings › Channel list: upcoming programmes** a panel above the
card lists the five programmes after NOW and NEXT, plus the programme at
primetime (20:15 by default). A description that doesn't fit the card scrolls
slowly, then starts again.

![Channel list with the EPG panel](docs/screenshots/channelselection-epg.jpg)

### TV guide

Timeline: translucent background and TiviMate-like grey cells; what is on now
is one shade lighter, the selected cell light grey, a red "now" line, and the
name of the channel you are watching in blue. Colours and font are passed to
the engine's EPG list through skin attributes (it used to show the engine's
default green/yellow blocks).

![EPG](docs/screenshots/epg-grid.jpg)

Multi EPG: Now / Next / Later tabs and a card for the selected programme.

![Multi EPG](docs/screenshots/epg-multi.jpg)

Single-channel EPG and event details with similar broadcasts.

<table>
<tr>
<td width="50%"><img src="docs/screenshots/epg-single.jpg" alt="Single-channel EPG"></td>
<td width="50%"><img src="docs/screenshots/event-view.jpg" alt="Event details"></td>
</tr>
</table>

### Channel menu

MENU in the channel list: a drawer that slides in from the right.

![Channel menu](docs/screenshots/channel-menu.jpg)

### Virtual keyboard

A sheet that opens from the bottom; the keys are not PNGs but boxes drawn by
the engine plus an icon font.

![Keyboard](docs/screenshots/keyboard.jpg)

### Menu

A translucent left panel that fades to the right over the picture, with a
white selection pill.

![Menu](docs/screenshots/menu.jpg)

### Settings

![Settings](docs/screenshots/setup.jpg)

### Timers

The recording list with a white selection pill; the card of the selected
programme on the right.

![Timers](docs/screenshots/timers.jpg)

### Plugins

The plugin browser in a grid, with colour key chips at the bottom.

![Plugins](docs/screenshots/plugins.jpg)

### Volume

A thin-edged pill above the infobar band: speaker glyph (`enigma2icons`), the
same fill as the progress lines, and the level. It sits where the infobar draws
almost nothing, because overlapping windows don't blend: lower down, the pill's
transparent corners would cut holes into the infobar while zapping. When muted, a round chip with just a red
muted-speaker glyph — no text, so it reads the same in every language.

![Volume](docs/screenshots/volume.jpg)

### Number zap

The number sits in its own tile, the channel name next to it. If the number
zap picon is enabled in the usage settings, the picon shows on the right
without a frame (the engine then looks for `NumberZapPicon`; the same design is
defined under that name too).

![Number zap](docs/screenshots/numberzap.jpg)

### Player

Elapsed and remaining time at both ends of the thin line; when paused, a status
pill top left (`PVRState`).

![Player](docs/screenshots/player.jpg)

### Enhanced Movie Center (EMC)

EMC's movie list, settings, menu and player are skinned: mini TV and the
recording's details on the left, the list on the right, the same keys and
cards as everywhere else.

![EMC movie list](docs/screenshots/emc.jpg)

### Colour keys

Instead of saturated coloured pills: a dark glass chip + coloured dot + white
text. The dot is a separate label bound to the same source as the key, so both
hide together when the key is empty. (The bottom rows in the screenshots.)

### Typefaces

The same infobar in the four bundled typefaces. Inter is the default; the
others are picked in the **TiviATV Font** plugin (see [Font](#font)).

![Typefaces](docs/screenshots/fonts.jpg)

### More screens

<table>
<tr>
<td width="50%"><img src="docs/screenshots/messagebox.jpg" alt="Message box"><br>Message box</td>
<td width="50%"><img src="docs/screenshots/inputbox.jpg" alt="Input box"><br>Input box</td>
</tr>
<tr>
<td><img src="docs/screenshots/pin.jpg" alt="Parental PIN"><br>Parental PIN</td>
<td><img src="docs/screenshots/mute.jpg" alt="Mute"><br>Mute</td>
</tr>
<tr>
<td><img src="docs/screenshots/console.jpg" alt="Console"><br>Console (package install)</td>
<td><img src="docs/screenshots/information.jpg" alt="Information"><br>Image information</td>
</tr>
<tr>
<td><img src="docs/screenshots/skin-settings.jpg" alt="Skin settings"><br>Skin settings</td>
<td><img src="docs/screenshots/font-picker.jpg" alt="Font picker"><br>Font picker</td>
</tr>
<tr>
<td><img src="docs/screenshots/hotkey-settings.jpg" alt="Hotkey settings"><br>Hotkey settings</td>
<td><img src="docs/screenshots/hotkey-functions.jpg" alt="Hotkey functions"><br>Hotkey settings: choosing a function</td>
</tr>
<tr>
<td><img src="docs/screenshots/input-devices.jpg" alt="Input devices"><br>Input devices</td>
<td><img src="docs/screenshots/locale.jpg" alt="Locale / language"><br>Locale / language</td>
</tr>
<tr>
<td><img src="docs/screenshots/emc-setup.jpg" alt="EMC settings"><br>EMC settings</td>
<td><img src="docs/screenshots/tiviatv-settings.jpg" alt="TiviATV Settings"><br>TiviATV Settings</td>
</tr>
<tr>
<td><img src="docs/screenshots/multiboot.jpg" alt="MultiBoot Manager"><br>MultiBoot Manager (sample slots)</td>
<td><img src="docs/screenshots/skin-setup.jpg" alt="Skin setup"><br>"Setup - TiviAtv-FHD" (openATV's AtileHD)</td>
</tr>
</table>

## Skinned screens

`InfoBar` · `SecondInfoBar` · `ChannelSelection` · `SimpleChannelSelection` ·
`ChannelSelectionRadio` · `EPGSelection` · `GraphicalEPG` · `GraphicalEPGPIG` ·
`EPGSelectionMulti` · `GraphMultiEPG` · `GraphMultiEPGList` · `EventView` ·
`Menu` · `Setup` · `MessageBox` · `ChoiceBox` · `Volume` ·
`Mute` · `NumberZap` · `NumberZapPicon` · `AudioSelection` · `SkinSelection` · `PluginBrowser` ·
`PackageAction` · `ChannelContextMenu` · `InputBox` · `PinInput` · `PinInputPopup` ·
`VirtualKeyBoard` · `Console` · `TextBox` · `Information` · `TimerEditList` ·
`MoviePlayer` · `PVRState` · `ButtonSetup` · `ButtonSetupSelect` · `InputDeviceSelection` ·
`LocaleSelection` · `MultiBootManager` · `KexecInit` · `AtileHD_Config` · `SubtitleDisplay` · `TiviAtvSettings` ·
`SimpleSummary`

EMC: `EMCSelection` · `EMCSelectionOwn` · `EnhancedMovieCenterMenu` · `MovieMenu` ·
`EMCMediaCenter` · `EMCMediaCenterOwn`

enigma2's standard colour names (`window-bg`, `window-fg`, `key_red`, `grey` …)
are also mapped to the skin palette. While they were undefined, every screen
without a counterpart in the skin — third-party plugins included — ran into a
`parseColor` error and ended up unreadable.

> The EPG screen names changed with openATV 8: `GraphicalEPG` /
> `GraphicalEPGPIG` / `EPGSelectionMulti` are looked up instead of
> `GraphMultiEPG`. The old names stay for the 7.3–7.5 branches.

Screens not defined here come from openATV's own `skin_default.xml`, so no
screen is ever left blank.

> `MessageBox` requires an `icon` widget: openATV's `skin.py`
> (`MANDATORY_WIDGETS`) rejects a screen with missing widgets and opens the
> default window instead. Check that list when adding a new screen.

### Other images (OpenViX)

Every widget is chosen at load time by the type of the component the screen
actually creates, so one skin serves both images:

- **Colour keys.** openATV creates `key_red` … as `StaticText` (a source); OpenViX
  creates many of them as `Button` (a GUI widget), and some older screens use
  `Label`. Binding a `Button` as a source with `ConditionalShowHide` throws in
  OpenViX's `skin.py`, and the loader then skips **the rest of the screen**. Each
  key therefore comes twice: for `StaticText` / `Boolean` a chip label (its text
  drawn in the chip colour, so invisible), the text label after the dot and the
  dot, all with `objectTypes="key_red,StaticText,Boolean"`; and for `Button` / `Label` an
  `eLabel` chip, a `name="key_red"` label that starts after the dot (OpenViX's
  `Button` ignores `textOffset`) and an `eLabel` dot, all with
  `objectTypes="key_red,Button,Label"`. Exactly one set is drawn. Neither set
  uses `padding`, which OpenViX doesn't support.
- **Plugin browser.** openATV 8 fills `pluginList` / `pluginGrid` (templates);
  OpenViX looks for a widget called `list` and draws the classic `PluginList`
  into it. The skin has both; `conditional` skips the one the image lacks. The
  classic rows are sized by the `PluginBrowserName` / `PluginBrowserDescr` /
  `PluginBrowserIcon` parameters and the `PluginBrowser0` / `PluginBrowser1`
  font aliases.
- Screens OpenViX names differently (for example its language selection) fall
  back to the image's own design.

![Plugin browser with the classic list and Button keys](docs/screenshots/plugins-classic.jpg)

`python3 tools/emulator/ekranlar.py <dir> pluginbrowser-vix` opens the same
skin screen the way OpenViX does (classic list, `Button` keys) in the openATV
emulator.

### PNG-free engine controls

Since 2026-09, openATV can draw some controls itself instead of using PNGs; the
skin turns them on in its `<parameters>` block:

| Parameter / attribute | Effect |
|---|---|
| `EPGNativeControls` | The "now" line and time lines in the graphical EPG and the multi EPG tabs become coloured labels |
| `VirtualKeyboardNative` | Virtual keyboard keys become rounded boxes + an `enigma2icons` glyph |
| `ChoiceListNative` | Number and bullet icons in ChoiceBox / channel menu rows |
| `iconFont` / `iconGlyphs` | MessageBox and player status icons from a font glyph |

Older images ignore these parameters: keys and icons are drawn with the
`skin_default` graphics, and two definitions for the time lines are picked with
`objectTypes` (a coloured line for a Label, the old PNG for a Pixmap).

## Customisation

### Colours

Changed in one place — the `<colors>` block at the top of
`TiviAtv-FHD/skin.xml`.

> **Alpha is inverted.** The format is `#AARRGGBB`, but `AA` = *transparency*:
> `00` is fully opaque, `FF` fully invisible. The trap people coming from CSS
> fall into most often.

Gradients **cannot** be defined in the `<colors>` block — `parseColor` only
accepts `#aarrggbb` there, and a comma-separated value silently falls back to
white. A gradient is written straight into the element's attribute; when
`backgroundColor` / `foregroundColor` contains a comma, it goes to
`parseGradient`:

```xml
<eLabel backgroundColor="#001c1c24,#00141419,vertical" />
```

Syntax: `start[,middle],end,vertical|horizontal[,alphaBlend]`

### Translucency

The panels over the picture are **flat translucent fills**: enigma2 writes the
fill's alpha into the pixel as is, and the box hardware composites the OSD
with the video layer — no extra CPU load. The `alphaBlend` flag at the end of a
gradient (`,1`), on the other hand, blends every pixel with what's below it on
the CPU; on boxes without graphics acceleration (e.g. Octagon SX88V2) it is not
used over large areas. Fades are gradients without the flag.

The translucent colours live in `<colors>`: `glass` (panel, 80 % opaque),
`glassSoft` (clock capsule), `card` (dialog / card), `chip` (badge), `scrim`
(dimming behind dialogs). Selection: `selBg` / `selFg` (white pill), `focus` /
`focusHi` (grey focus). Lines: `track` (background of progress and scroll
bars), `edge` (the 2 px edge of cards and chips).

> On an `eLabel`, a box edge is drawn with `widgetBorderWidth` /
> `widgetBorderColor`. `borderWidth` / `borderColor` there is the outline of the
> text (`elabel.h`); `lint_skin.py` warns about it.

> Overlapping windows don't blend either: the top window's pixel replaces the
> one below. Behind a translucent card you see the picture, not the screen
> underneath.

### Softcam (ECM) info

The infobar shows the softcam's ECM info by itself — there is nothing to set
up in the skin. OSCam (and most other softcams) write `/tmp/ecm.info` for the
channel being decoded; the `TiviAtvEcm` converter reads it once a second, and
only when the file changes:

```
Irdeto 0604  ·  my_reader  ·  newcamd  ·  1 hop  ·  0.214 s
```

- It appears only on **encrypted** channels, and only while the softcam has
  written `/tmp/ecm.info`. On free-to-air channels the corner stays empty.
- It follows **Menu › Setup › Usage & GUI › OSD Settings › Show crypto info in
  InfoBar**: `Off` hides it, `One line` / `Two lines` show it (the default is
  on; the item is listed at the *Expert* setup level).
- **Hide softcam servername** in the same screen hides the server address
  (`•••`) when the card is shared over the network.
- The system name comes from the CAID when the softcam doesn't write one, and
  the ECM time is shown in seconds whether the softcam writes seconds or
  milliseconds.
- Long reader / server names are shortened to 24 characters, and a line that
  still doesn't fit ends with `…` — the start (system and CAID) always stays
  visible.

![Long server name, shortened](docs/screenshots/infobar-ecm-long.jpg)

The widget sits in the `InfoBar` screen (`<convert type="TiviAtvEcm" />`), so it
can be moved or restyled like any other label.

### TiviATV Settings

**Menu › Setup › Usage & GUI › TiviATV Settings** (also in the plugin
browser). Changes apply at once, no GUI restart:

| Option | Default | What it does |
|---|---|---|
| Channel list: upcoming programmes | No | Panel above the programme card: the 5 programmes after NOW and NEXT |
| Primetime | 20:15 | The programme on at that time (today, or tomorrow once it is over) at the bottom of the panel; Off hides the row |
| Scroll long descriptions | Yes | The channel list description scrolls when it doesn't fit |

The values are stored in `config.plugins.TiviAtv`; the panel's widgets read
them through the `TiviAtvEpg` converter, so a skin edit can move or restyle
the panel freely.

### Subtitles

DVB, teletext and text subtitles are drawn into the `SubtitleDisplay` window.
The skin defines it as `size="e,e"`, so it always covers the whole OSD —
720p, 1080p, 4K or 8K. (openATV's default definition is 1280×720, which on a
1080p skin put the subtitles in the middle of the screen.) Position and size
come from enigma2's own subtitle settings.

![Subtitles at the bottom of the picture](docs/screenshots/subtitles.jpg)

### Rounded corners

```xml
cornerRadius="24"                   <!-- all four corners -->
cornerRadius="3;left"               <!-- left only -->
cornerRadius="30;topLeft,topRight"  <!-- selected corners -->
```

Valid corner names: `topLeft` `topRight` `top` `bottomLeft` `bottomRight`
`bottom` `left` `right`

### Font

The default typeface is **Inter**: a grotesque drawn for screen interfaces,
readable from a distance thanks to its large x-height, with complete Turkish
characters. The folder has four weights (Regular / Medium / SemiBold / Bold →
`TM` / `TMM` / `TMB` / `TMX`), made static from the variable font at
`opsz=22` — between the comfortable spacing of the text cut (14) and the
tightness of the display cut (32). The second modern option in the picker is
**Geist**, plus Barlow and the old Sony Sketch.

The skin's measurements were laid out for a narrow font, so wider families are
scaled down in `fonts.xml`: Inter `scale="92"`, Geist `scale="94"` (the engine
applies size × scale / 100). The plugin writes this scale itself when it picks
a family.

The active typeface is not in `skin.xml` but in a separate `fonts.xml`, which
`skin.xml` loads with `<include filename="fonts.xml" />`. The font names used in
the skin (`TM` / `TMM` / `TMB` / `TMX`) never change, only the `.ttf` files they
point to.

To change it on the box, open the plugin that comes with the package: **Menu →
Setup → Usage & GUI → TiviATV Font** lists the fonts in the skin folder
and under `/usr/share/fonts`; the chosen family is written to `fonts.xml` and
the GUI restarts. If a family has several weights (like Inter's four), the four
slots are matched automatically; a single-weight font is used for all four.
Glyph fonts such as `enigma2icons` are not listed.

![Font picker](docs/screenshots/font-picker.jpg)

The list is enigma2's `ChoiceBox` screen — its look comes from this skin's
`<screen name="ChoiceBox">`, the plugin has no embedded skin. `fonts.xml` can
also be edited by hand.

## Tools

Run from the repository root; none of them has a hard-coded path.

| Script | What it does |
|---|---|
| `tools/lint_skin.py` | Checks the skin against openATV's **real** attribute list — downloads `skin.py` and `ServiceList.py` from upstream and parses them. Catches undefined colours/fonts, elements that overflow the screen, unknown attributes, and a text outline mistaken for a box edge on an `eLabel`. |
| `tools/render_preview.py` | Builds `preview.html` — draws the screens in the browser from skin.xml's real coordinates, colours and radii. |
| `tools/make_thumb.py` | Builds the skin selector's `prev.png` from the emulator's channel list screenshot. |
| `tools/build_ipk.py` | Builds the installation package (`dist/*.ipk` + `.sha256`); runs lint, a Python compile and a `fonts.xml` check first. The same sources always give the same package. |
| `tools/make_fonts.py` | Makes Inter's and Geist's static weights from the variable fonts on Google Fonts (enigma2 can't pick a weight in a variable font). |
| `tools/make_designer_copy.py` | Builds an OpenSkin Designer compatible copy (see below). |
| `tools/emulator/` | Skin testing in the PC emulator: sample channels/EPG, a test stream, screenshots of every screen (see below). |

Requirements: Python 3.9+, `Pillow` (`make_thumb.py`) and `fonttools`
(`make_fonts.py`).

```bash
pip install pillow fonttools
```

### Releasing

1. Bump `VERSION` and commit it with the changes.
2. `python3 tools/build_ipk.py` → a new package under `dist/` (the old one is
   removed).
3. Commit `dist/` and push to `main`; `installer.sh` reads the version from
   `VERSION`, so boxes get the new package the next time they run it.

## Testing in the emulator

Tested without a box, on OpenATV enigma2 built for the PC (SDL2). The emulator
itself is set up with `tools/e2pc/kur.sh` from the FY Sinema repository
(`e2-arkaplan`, `e2-tus` and `e2-ekran` come from there); this folder adds the
parts specific to skin testing:

| File | What it does |
|---|---|
| `TiviAtvTest/` | A plugin installed only in the emulator: runs the Python code in `/tmp/e2py.cmd` inside enigma2 and loads the sample EPG at startup. It is **not** installed on the box. |
| `e2-py` | Sends code to that plugin: `e2-py 'session.open(...)'` |
| `demo_kanallar.py` | Writes a 16-channel sample list (4 Türksat 42E + 12 IPTV), EPG, picons and a test stream (with enigma2 stopped) |
| `e2-yayin` | The test stream the IPTV channels play (`127.0.0.1:8099`, ffmpeg) |
| `ekranlar.py` | Opens the screens one by one without navigating the menus and takes their screenshots |

```bash
ln -sfn $PWD/TiviAtv-FHD /usr/share/enigma2/TiviAtv-FHD
ln -sf  $PWD/TiviAtv-FHD/converter/*.py /usr/lib/enigma2/python/Components/Converter/
ln -sf  $PWD/TiviAtv-FHD/renderer/*.py /usr/lib/enigma2/python/Components/Renderer/
ln -sfn $PWD/tools/emulator/TiviAtvTest /usr/lib/enigma2/python/Plugins/Extensions/TiviAtvTest
python3 tools/emulator/demo_kanallar.py && tools/emulator/e2-yayin && e2-arkaplan
python3 tools/emulator/ekranlar.py                 # all  -> .cache/ekranlar/
python3 tools/emulator/ekranlar.py /tmp/ss menu epgselection
python3 tools/emulator/ekranlar.py --kare frame.jpg /tmp/ss   # lay the OSD over a sample frame
```

## OpenSkin Designer notes

[OpenSkin Designer](https://github.com/iMaxxx/OpenSkin-Designer) dates from
2014 and can't open the skin as is. `tools/make_designer_copy.py` builds a
compatible copy:

| Problem | Why | In the copy |
|---|---|---|
| `<alias>` | `cDataBase.initFonts` reads `filename` from **every** child of `<fonts>`, with no node name filter → `NullReferenceException` | removed |
| XML comments inside blocks | A comment node has no attributes, same crash | removed |
| Gradient colour values | `#a,#b,vertical` can't be parsed as a colour | the average of the two stops |
| `listbox`/`label`/`configList`/`scrolllabel` inside `<windowstyle>` | Not in the working sample skins, no `name` attribute | removed |

The string `cornerRadius` doesn't appear anywhere in the program's binary — the
skin **always shows square corners** in the designer. The rounding only appears
on the box, when enigma2 draws it.

```bash
python tools/make_designer_copy.py
```

## Changelog

**1.0.6**
- Volume and mute moved up, above the infobar band: while zapping, their round
  corners no longer cut into the infobar.
- OpenViX: colour key labels start after the dot on every screen (the chips no
  longer rely on `padding`, which OpenViX ignores) — TiviATV Settings included.
- openATV's "Setup - TiviAtv-FHD" screen (AtileHD) skinned; the colour name
  `foreground` is the light text colour, so its key labels — and those of other
  plugins using it — are readable.

**1.0.5**
- MultiBoot Manager (Standby / Restart) and its Kexec / Chkroot set-up window
  use the large translucent settings card with colour key chips.

**1.0.4**
- Subtitles: DVB and teletext subtitles were in the middle of the screen; the
  subtitle window now covers the whole OSD at any resolution.
- Enhanced Movie Center: movie list, settings, menu and player skinned. On
  screens the skin doesn't define (EMC's settings page was one), lists no longer
  punch a transparent hole into the window.
- Channel list: optional EPG panel with the next 5 programmes and primetime,
  and long descriptions scroll — **TiviATV Settings**, a new entry next to
  TiviATV Font.
- Softcam line: long reader / server names no longer push the start of the
  line out of view.
- OpenViX: colour key labels no longer run under the coloured dot.

**1.0.3**
- OpenViX: the plugin browser was empty — it draws into a classic `list`
  widget, which the skin now has. Colour keys created as `Button` / `Label`
  (OpenViX channel list, EPG, event view, plugins …) get their own chips;
  before, they stopped the rest of the screen from loading.

**1.0.2**
- Softcam ECM info in the infobar (OSCam, CCcam …), on encrypted channels only:
  system + CAID, reader, protocol, hops and ECM time from `/tmp/ecm.info`
  (new `TiviAtvEcm` converter). See [Softcam (ECM) info](#softcam-ecm-info).
- Hotkey settings, input devices and locale / language screens restyled:
  large translucent cards like the other settings screens, colour key chips,
  flags and status icons in the language list.

**1.0.1**
- Everything shown on the box is in English: labels (NOW, NEXT, LATER),
  screen titles, the font picker (now **TiviATV Font**), the installer and the
  package messages. The mute indicator is an icon-only chip (no text to
  translate), and the NOW chip fits longer translations such as MAINTENANT. Labels and titles follow the box's GUI language through
  enigma2's own translations; the font picker and the signal percentages
  (86% / %86) switch to Turkish on a Turkish GUI.
- Screenshots retaken with English sample data.

**1.0.0**
- First release as an installable package: one-line installer, opkg package
  with the skin, two converters and the font picker.
- Inter as the default typeface, plus Geist, Barlow and Sony Sketch.
- Thin progress lines, colour key chips, edged cards; TiviMate layout with
  translucent panels.

## License

Skin files are MIT — see [LICENSE](LICENSE).
The Inter, Geist and Barlow typefaces are under the SIL Open Font License 1.1,
see `OFL-Inter.txt`, `OFL-Geist.txt`, `OFL-Barlow.txt`. Inter's and Geist's
static weights were made from the variable fonts on Google Fonts with
`fontTools` (the OFL allows modified versions; neither family has a Reserved
Font Name).
`Sony_Sketch_Bold_205.ttf` is a third-party font; its distribution rights are
outside the scope of the skin's license.
Channel logos (picons) are not included in the skin; they are installed
separately under `/usr/share/enigma2/picon/`.
