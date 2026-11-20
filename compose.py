#!/usr/bin/env python3
"""Compose the front page for make.fun news-image-20261120.

Builds assets/entry.png (1024x1024) from 13 original illustration panels
plus typography drawn with PIL. All 43 stories were verified as Friday
20 November 2026 events; near-miss 19 Nov stories are named in the
DATE CHECK box, never as news.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
PANELS = os.path.join(BASE, "panels")
OUT = os.path.join(BASE, "assets", "entry.png")
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

W, H = 1024, 1024
CREAM = (246, 241, 227)
NAVY = (14, 42, 71)
INK = (26, 26, 26)
RED = (163, 30, 34)
GRAY = (91, 113, 134)
LIGHT = (237, 230, 210)
SEA = (217, 228, 235)
LAND = (234, 223, 194)
RULE = (201, 191, 166)
WHITE = (255, 255, 255)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)


def wrap(d, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(d, text, fnt, width, max_lines, shrink_to=None):
    """Wrap text; shrink font until it fits max_lines. Returns (lines, font)."""
    size = fnt.size
    floor = shrink_to if shrink_to else max(8, size - 4)
    while size >= floor:
        f = font(fnt.path, size) if hasattr(fnt, "path") else fnt
        lines = wrap(d, text, f, width)
        if len(lines) <= max_lines:
            return lines, f
        size -= 1
    f = font(fnt.path, floor) if hasattr(fnt, "path") else fnt
    return wrap(d, text, f, width)[:max_lines], f


def paste_panel(img, path, box):
    """Center-crop panel to box aspect, resize, paste, 1px navy border."""
    x0, y0, x1, y1 = box
    tw, th = x1 - x0, y1 - y0
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    target = tw / th
    src = iw / ih
    if src > target:  # too wide: crop sides
        nw = int(ih * target)
        left = (iw - nw) // 2
        im = im.crop((left, 0, left + nw, ih))
    else:  # too tall: crop top/bottom (keep upper 60% for skies)
        nh = int(iw / target)
        top = int((ih - nh) * 0.35)
        im = im.crop((0, top, iw, top + nh))
    im = im.resize((tw, th), Image.LANCZOS)
    img.paste(im, (x0, y0))
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1 - 1, y1 - 1], outline=NAVY, width=1)


# ---------------------------------------------------------------- stories
BIG3 = [
    dict(pin=1, file="01-brussels.webp", kicker="1 · BRUSSELS — SUMMIT",
         head="UK and EU strike youth-mobility deal at Brussels summit",
         deck="Britain will issue 100,000 visas a year to young Europeans, and "
              "Britons get the same in return, in the biggest reset of ties since "
              "Brexit. Food checks go; carbon markets link."),
    dict(pin=2, file="02-taipei.webp", kicker="2 · TAIPEI — MARKETS",
         head="Taiwan shares plunge 2,200 points as AI-bubble fear sweeps Asia",
         deck="Taipei's benchmark dives below 37,000 and has shed 7,000 points in "
              "a week. SoftBank slides in Tokyo as the great AI trade unwinds."),
    dict(pin=3, file="03-akvan.webp", kicker="3 · ODISHA — WEATHER",
         head="Cyclone Akvan comes ashore in Odisha",
         deck="The season's third cyclone crosses the coast near Gopalpur with "
              "winds of 70–80 km/h. More than 300,000 people were moved to "
              "shelters; no deaths were reported at first count."),
]

GRID = [
    dict(pin=4, file="04-kyiv.webp", head="Russian missiles hit three Kyiv bridges; three killed"),
    dict(pin=5, file="05-berlin.webp", head="Kyiv: no deal without us, allies pledge more aid"),
    dict(pin=6, file="06-gaza.webp", head="Israel's Gaza operation crosses the ceasefire line"),
    dict(pin=7, file="07-istanbul.webp", head="Turkish court bars jailed Istanbul mayor from 2028 race"),
    dict(pin=8, file="08-drones.webp", head="Britain pledges 1,000-plus drones for Ukraine"),
    dict(pin=9, file="09-sanctions.webp", head="US sanctions Comancheros and 'Ndrangheta"),
    dict(pin=10, file="10-b2.webp", head="B-2 pilots tell how Midnight Hammer unfolded"),
    dict(pin=11, file="11-florida.webp", head="Florida carries out a record 20th execution"),
    dict(pin=12, file="12-genoa.webp", head="Drones halt flights at Genoa airport"),
    dict(pin=13, file="13-chip.webp", head="California opens probe into Nvidia's China chip sales"),
]

NUMBERS = [
    ("100,000", "YOUTH VISAS A YEAR — UK–EU DEAL"),
    ("2,200", "POINTS LOST BY TAIWAN STOCKS"),
    ("3", "KYIV BRIDGES HIT BY MISSILES"),
    ("1,000+", "DRONES PLEDGED FOR UKRAINE"),
    ("880,000", "AI CHIPS CLEARED FOR CHINA"),
    ("300,000", "EVACUATED BEFORE CYCLONE AKVAN"),
]

REGIONS = "ASIA 5 · EUROPE 10 · AMERICAS 17 · MIDDLE EAST 7 · AFRICA 2 · OCEANIA 1 · GLOBAL 1"

BRIEFS = [
    "UN chief race: ninth ballot due as deadlock drags on.",
    "Iraqi troops move in as militia deadline expires.",
    "Harris meets Macron in Paris for a courtesy call.",
    "Boat capsizes off Senegal; four dead.",
    "Fuel shortages spark violence in Malawi.",
    "Meta waters down its 2030 climate targets.",
    "Poland lines up a $50bn nuclear deal with US firms.",
    "Czech leaders visit Israel to talk defence.",
    "Chicago man denies Hindu temple shooting plot.",
    "White House tells press to bag phones on China flight.",
    "Magnitude 5.6 quake strikes near New Caledonia.",
    "America's war with Iran has cost $48bn and counting.",
    "Saudi Arabia warns of thunderstorms and flash floods.",
    "Samsung names a new chief for its mobile division.",
    "Broadcom patches a critical VMware vCenter flaw.",
    "House panel: 880,000 advanced AI chips cleared for China.",
    "Anthropic slips on day two as the AI sell-off deepens.",
    "Quebecor bids C$31bn for Canadian carrier Telus.",
    "Japan core inflation hits 2.2%, a high for the year.",
    "Lula visits ailing Chief Raoni as land rights advance.",
    "Six killed in a gas blast at a Tbilisi apartment block.",
    "One dead, 15 hurt in a fire at a French tower block.",
    "Israeli jets hit a Hezbollah missile site in Lebanon.",
    "US court curbs agriculture chief's religious emails.",
    "Google's Gemini can now drive a Mac.",
    "Democrats: law firm did $11.8m of free work for Trump.",
    "Saudi defences shoot down two Houthi drones.",
    "Fiona the hippo dies at Cincinnati Zoo after eating a hat.",
    "China warns climbers off Mount Fuji as family offers reward.",
    "Merz: fresh Ukraine talks with Europe to be held soon.",
]

DATE_CHECK = (
    "DATE CHECK — NOT TODAY: Shenzhen summit & peace declaration · Anthropic's Nasdaq debut, "
    "+17% · Pete Rose pardon · US–Venezuela military deal · COP31 draft drops fossil fuels · "
    "Mongolia's president resigns · Bangladesh lockdown violence · Denmark ratifies Greenland "
    "deal · 589m children in conflict zones · Kyiv embassy strikes · Houthi strikes on Riyadh, "
    "tankers mined · Haiti raid kills 34 · Bukele registers for third term · Pew: Islam largest "
    "faith by 2035 — all Thu 19 Nov (Venezuela deal Wed 18 Nov; Pew study Wed 18 Nov)."
)

FOOTER = ("Sources: Reuters · The Times · BBC · AP · AFP · IMD · Bloomberg · Pew · Save the Children · "
          "UN News · Le Monde — see NEWS.md. All 43 stories date-checked to Friday 20 November 2026.")

# Map pins: (story number, lon, lat) — a few nudged so circles don't collide.
PINS = [
    (1, 4.5, 48.0), (2, 121.56, 25.03), (3, 84.9, 19.27), (4, 30.52, 50.45),
    (5, 15.5, 53.5), (6, 39.0, 27.5), (7, 33.5, 37.5), (8, -3.0, 53.0),
    (9, -77.04, 38.9), (10, -93.55, 38.73), (11, -84.28, 30.44),
    (12, 11.0, 42.0), (13, -121.49, 38.58),
]

PIN_KEY = [
    "Brussels — UK–EU summit", "Taipei — stocks plunge", "Odisha — Cyclone Akvan",
    "Kyiv — bridges hit", "Berlin — allies pledge aid", "Gaza — ceasefire-line op",
    "Istanbul — mayor barred", "London — drones for Ukraine", "Washington — US sanctions",
    "Missouri — B-2 pilots", "Florida — 20th execution", "Genoa — airport drones",
    "California — Nvidia probe",
]

# Simplified continent outlines (lon, lat).
NORTH_AMERICA = [(-168, 66), (-156, 58), (-148, 61), (-140, 60), (-134, 57), (-128, 51),
    (-124, 48), (-124, 42), (-121, 37), (-117, 33), (-112, 29), (-108, 25), (-105, 21),
    (-100, 18), (-96, 16), (-93, 15), (-89, 14), (-85, 12), (-82, 9), (-79, 9), (-77, 8),
    (-79, 10), (-82, 13), (-86, 16), (-88, 17), (-90, 21), (-92, 19), (-95, 19), (-97, 26),
    (-94, 29), (-90, 29), (-85, 30), (-81, 26), (-80, 31), (-77, 34), (-75, 38), (-74, 41),
    (-70, 43), (-67, 45), (-63, 44), (-59, 47), (-54, 48), (-53, 50), (-56, 52), (-60, 55),
    (-64, 58), (-68, 60), (-73, 62), (-79, 63), (-85, 66), (-92, 66), (-96, 69), (-108, 68),
    (-120, 69), (-133, 70), (-145, 70), (-157, 71), (-165, 68)]
SOUTH_AMERICA = [(-77, 7), (-75, 10), (-72, 12), (-68, 11), (-64, 10), (-60, 8), (-55, 6),
    (-52, 5), (-50, 0), (-48, -3), (-44, -3), (-41, -6), (-38, -8), (-35, -9), (-37, -13),
    (-39, -17), (-40, -22), (-46, -24), (-49, -28), (-52, -33), (-55, -35), (-58, -38),
    (-62, -41), (-66, -45), (-68, -50), (-69, -52), (-71, -54), (-73, -50), (-73, -44),
    (-73, -38), (-72, -32), (-71, -25), (-70, -19), (-75, -15), (-79, -9), (-81, -5),
    (-80, 0), (-80, 3), (-77, 5)]
AFRICA = [(-17, 15), (-16, 20), (-15, 24), (-13, 27), (-10, 29), (-6, 33), (-2, 35), (3, 37),
    (10, 37), (11, 34), (15, 32), (19, 30), (25, 32), (30, 31), (32, 31), (34, 28), (35, 24),
    (37, 20), (39, 18), (40, 15), (43, 12), (46, 11), (51, 12), (51, 10), (48, 6), (44, 2),
    (41, -2), (40, -6), (39, -10), (37, -14), (35, -18), (33, -22), (32, -26), (29, -29),
    (26, -33), (20, -35), (17, -32), (15, -28), (13, -22), (12, -17), (13, -12), (12, -6),
    (9, -1), (9, 4), (4, 6), (-2, 5), (-8, 5), (-13, 8), (-16, 12)]
EURASIA = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 49), (0, 50),
    (3, 53), (7, 54), (8, 57), (10, 59), (6, 62), (12, 64), (18, 66), (21, 70), (25, 71),
    (30, 70), (35, 68), (40, 68), (45, 68), (52, 69), (58, 69), (66, 69), (73, 72), (80, 73),
    (90, 75), (100, 76), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (158, 69),
    (162, 66), (170, 66), (178, 65), (178, 62), (170, 60), (162, 58), (158, 53), (156, 51),
    (150, 59), (142, 55), (140, 48), (138, 42), (135, 38), (130, 35), (127, 35), (122, 32),
    (120, 28), (118, 25), (112, 22), (108, 18), (105, 10), (103, 7), (100, 6), (98, 10),
    (96, 16), (94, 17), (92, 21), (89, 22), (86, 20), (84, 19), (80, 16), (77, 8), (76, 10),
    (73, 16), (70, 20), (67, 24), (64, 25), (60, 25), (57, 26), (54, 26), (52, 28), (50, 29),
    (48, 30), (48, 24), (44, 18), (42, 15), (40, 13), (38, 20), (35, 28), (34, 31), (33, 36),
    (30, 36), (27, 37), (23, 36), (22, 38), (19, 40), (16, 38), (14, 42), (12, 44), (8, 44),
    (6, 43), (3, 42), (0, 40), (-2, 37), (-6, 36), (-9, 37)]
AUSTRALIA = [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32), (132, -32),
    (135, -35), (138, -35), (140, -38), (144, -38), (147, -39), (150, -37), (153, -32),
    (153, -27), (151, -24), (148, -20), (146, -19), (142, -15), (142, -11), (140, -17),
    (136, -15), (135, -12), (132, -11), (130, -13), (126, -14), (122, -17), (118, -20)]
ISLANDS = [  # (lon, lat, rx, ry) in degrees
    (-2, 54, 3, 4), (139, 37, 2, 5), (172, -41, 2, 4), (115, -3, 6, 2),
    (47, -19, 2, 5), (-42, 72, 8, 6), (-18, 65, 3, 2), (80, 7, 1.5, 2),
    (121, 23.5, 1.5, 2.5),
]


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    MX = 16
    CW = 992  # content width

    # ---------------------------------------------------------- masthead
    f_top = SANS_B(9)
    d.text((MX, 10), "ONE IMAGE · THE WHOLE DAY", font=f_top, fill=NAVY)
    right = "FRIDAY 20 NOVEMBER 2026"
    d.text((W - MX - d.textlength(right, font=f_top), 10), right, font=f_top, fill=NAVY)
    d.line([(MX, 26), (W - MX, 26)], fill=NAVY, width=1)
    f_title = SERIF_B(56)
    title = "THE WORLD TODAY"
    d.text(((W - d.textlength(title, font=f_title)) / 2, 30), title, font=f_title, fill=NAVY)
    f_date = SERIF_B(15)
    date = "FRIDAY, 20 NOVEMBER 2026  ·  43 STORIES  ·  ALL DATE-CHECKED"
    d.text(((W - d.textlength(date, font=f_date)) / 2, 82), date, font=f_date, fill=INK)
    d.line([(MX, 100), (W - MX, 100)], fill=NAVY, width=2)
    d.line([(MX, 103), (W - MX, 103)], fill=NAVY, width=1)

    # ---------------------------------------------------------- big three
    col_x = [16, 350, 684]
    col_w = 322
    for i, s in enumerate(BIG3):
        x = col_x[i]
        d.text((x, 110), s["kicker"], font=SANS_B(10), fill=RED)
        paste_panel(img, os.path.join(PANELS, s["file"]), (x, 126, x + col_w, 246))
        lines, f = fit_text(d, s["head"], SERIF_B(16), col_w, 3, shrink_to=14)
        y = 252
        for ln in lines:
            d.text((x, y), ln, font=f, fill=INK)
            y += 19
        lines, f = fit_text(d, s["deck"], SANS(10), col_w, 3, shrink_to=9)
        y = 304
        for ln in lines:
            d.text((x, y), ln, font=f, fill=(58, 58, 58))
            y += 13
    d.line([(MX, 350), (W - MX, 350)], fill=RULE, width=1)

    # ---------------------------------------------------------- numbers strip
    d.rectangle([MX, 356, W - MX, 406], fill=NAVY)
    cell_w = CW / 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = MX + cell_w * i + cell_w / 2
        f_num = SERIF_B(23)
        d.text((cx - d.textlength(num, font=f_num) / 2, 363), num, font=f_num, fill=CREAM)
        f_lab = SANS(8)
        d.text((cx - d.textlength(label, font=f_lab) / 2, 392), label, font=f_lab, fill=(214, 222, 232))
        if i:
            d.line([(MX + cell_w * i, 364), (MX + cell_w * i, 398)], fill=(60, 84, 110), width=1)

    # ---------------------------------------------------------- region strip
    d.rectangle([MX, 412, W - MX, 438], fill=LIGHT)
    f_reg = SANS_B(10)
    reg = "WHERE THE NEWS CAME FROM   " + REGIONS
    d.text(((W - d.textlength(reg, font=f_reg)) / 2, 421), reg, font=f_reg, fill=NAVY)

    # ---------------------------------------------------------- grid of ten
    d.text((MX, 444), "TEN MORE STORIES", font=SANS_B(11), fill=NAVY)
    d.line([(MX + 150, 450), (W - MX, 450)], fill=RULE, width=1)
    gw, gut = 192, 8
    for i, s in enumerate(GRID):
        row, col = divmod(i, 5)
        x = MX + col * (gw + gut)
        y = 462 + row * 100
        paste_panel(img, os.path.join(PANELS, s["file"]), (x, y, x + gw, y + 70))
        lines, f = fit_text(d, s["head"], SERIF_B(11), gw, 2, shrink_to=10)
        yy = y + 74
        for ln in lines:
            d.text((x, yy), ln, font=f, fill=INK)
            yy += 13

    # ---------------------------------------------------------- world map
    d.text((MX, 668), "WHERE IT HAPPENED", font=SANS_B(11), fill=NAVY)
    d.text((MX + 158, 669), "— the 13 illustrated stories, numbered as they appear above",
           font=SANS(9), fill=GRAY)
    d.line([(MX, 684), (W - MX, 684)], fill=RULE, width=1)
    map_x0, map_y0, map_x1, map_y1 = MX, 688, 656, 830
    d.rectangle([map_x0, map_y0, map_x1, map_y1], fill=SEA, outline=NAVY, width=1)

    def proj(lon, lat):
        x = map_x0 + (lon + 170) / 360 * (map_x1 - map_x0)
        y = map_y0 + (80 - lat) / 125 * (map_y1 - map_y0)
        return x, y

    for poly in (NORTH_AMERICA, SOUTH_AMERICA, AFRICA, EURASIA, AUSTRALIA):
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND, outline=NAVY)
    for lon, lat, rx, ry in ISLANDS:
        cx, cy = proj(lon, lat)
        sx = rx / 360 * (map_x1 - map_x0)
        sy = ry / 125 * (map_y1 - map_y0)
        d.ellipse([cx - sx, cy - sy, cx + sx, cy + sy], fill=LAND, outline=NAVY)
    f_pin = SANS_B(7)
    for num, lon, lat in PINS:
        cx, cy = proj(lon, lat)
        r = 6
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=WHITE, width=1)
        t = str(num)
        d.text((cx - d.textlength(t, font=f_pin) / 2, cy - 5), t, font=f_pin, fill=WHITE)

    # pin key: number + place for each illustrated story
    kx = 672
    d.text((kx, 688), "PIN KEY", font=SANS_B(10), fill=NAVY)
    d.line([(kx, 702), (W - MX, 702)], fill=RULE, width=1)
    f_key = SANS(9)
    f_keyn = SANS_B(9)
    for i, label in enumerate(PIN_KEY):
        y = 706 + i * 9.5
        d.text((kx, y), f"{i + 1}", font=f_keyn, fill=RED)
        d.text((kx + 20, y), label, font=f_key, fill=INK)

    # ---------------------------------------------------------- briefs
    d.text((MX, 836), "THE DAY IN BRIEF", font=SANS_B(11), fill=NAVY)
    d.line([(MX + 138, 842), (W - MX, 842)], fill=RULE, width=1)
    f_brief = SANS(9)
    for i, b in enumerate(BRIEFS):
        col, row = divmod(i, 10)
        x = MX + col * (col_w + 12)
        y = 852 + row * 10.5
        d.text((x, y), f"{i + 1}. {b}", font=f_brief, fill=INK)

    # ---------------------------------------------------------- date check
    d.rectangle([MX, 962, W - MX, 1004], fill=LIGHT, outline=NAVY, width=1)
    lines = wrap(d, DATE_CHECK, SANS(8), CW - 20)
    y = 966
    for ln in lines:
        d.text((MX + 10, y), ln, font=SANS(8), fill=INK)
        y += 10
    print(f"date-check lines: {len(lines)} (box fits 4)")

    # ---------------------------------------------------------- footer
    f_foot = SANS(8)
    d.text(((W - d.textlength(FOOTER, font=f_foot)) / 2, 1008), FOOTER, font=f_foot, fill=GRAY)

    # ---------------------------------------------------------- save
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, optimize=True)
    size = os.path.getsize(OUT)
    print(f"saved {OUT}: {img.size}, {size} bytes")
    if size > 1_048_576:
        print("over 1 MiB — quantizing to 256-color palette")
        q = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
        q.save(OUT, optimize=True)
        size = os.path.getsize(OUT)
        print(f"quantized: {size} bytes")
    assert img.size == (1024, 1024), img.size
    assert size <= 1_048_576, size
    print("OK")


if __name__ == "__main__":
    main()
