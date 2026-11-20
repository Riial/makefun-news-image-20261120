#!/usr/bin/env python3
"""Build the v2 front page for news-image-20261120: Friday 20 November 2026.

Renders one 1024x1024 newspaper-style image with PIL and writes it to
assets/entry.png next to this file. The entry program (main.py) only copies
that file to /output/entry.png. Every story below was date-checked against
primary reporting for 20 November 2026 in this session; items that turned
out to be Thursday 19 November news live in the DATE CHECK box, not in the
day's stories.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "entry.png")

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (17, 17, 17)
GREY = (96, 92, 84)
FAINT = (150, 145, 134)
RED = (176, 30, 36)
NAVY = (20, 33, 61)
NAVY2 = (15, 32, 64)
LAND = (58, 92, 143)
TEAL = (13, 66, 66)
TEAL_LT = (64, 150, 150)
GREEN = (27, 68, 42)
GREEN_LT = (120, 180, 120)
GOLD = (255, 210, 63)
CREAM = (250, 246, 238)
RULE = (17, 17, 17)

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FD, "liberation", "LiberationSerif-Bold.ttf")
SERIF = os.path.join(FD, "liberation", "LiberationSerif-Regular.ttf")
SERIF_I = os.path.join(FD, "liberation", "LiberationSerif-Italic.ttf")
SANS_B = os.path.join(FD, "dejavu", "DejaVuSans-Bold.ttf")
SANS = os.path.join(FD, "dejavu", "DejaVuSans.ttf")


def F(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- helpers
def wrap(text, font, max_w, draw):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, font, fill=INK, leading=None, align="left",
               width=None):
    """Draw lines starting at (x, y); returns y after the last line."""
    if leading is None:
        leading = font.size + 2
    for line in lines:
        if align == "center" and width is not None:
            lx = x + (width - draw.textlength(line, font=font)) // 2
        elif align == "right" and width is not None:
            lx = x + width - draw.textlength(line, font=font)
        else:
            lx = x
        draw.text((lx, y), line, font=font, fill=fill)
        y += leading
    return y


def hline(draw, x0, x1, y, fill=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def kicker(draw, x, y, label, color=RED, size=11):
    f = F(SANS_B, size)
    draw.text((x, y), label, font=f, fill=color)
    return y + size + 3


# ------------------------------------------------------- world land mask
# 96 columns (lon -180..180) x 36 rows (lat 75..-55). '#' = land.
# Stylised dotted-map mask, drawn from general geography.
LANDMASK = [
    ".................................#######..............................................",
    "....#######...##############.......#########......###################################.",
    "...##########..################...##########....#####################################",
    "....########..#################....########..#.#########..############################",
    ".....#######...###############......######......#########..###########################.",
    "......######...###############....##...######...########################################",
    "......######....#############....###...#######..#######################################",
    ".......######....###########....##############..######################################.",
    ".......######.....#########....###############..####################################...",
    "........######.....########....##############...##################################.....",
    "........######.....#######.....#############....###############################.#.......",
    ".........######....#######.....############......##########################.............",
    ".........######....######......###########.......#######################..............",
    ".........######....#####.......##########........######################...............",
    "..........#####....#####.......#########.........#####################................",
    "..........#####....#####.......########..........###################..................",
    "...........####....####........########..........##################...................",
    "............###....###.........########...........#################..................",
    "............###...####.........#########..........################...................",
    "............###...####.........########...........###############....................",
    "............###...#####.........#######...........##############.....................",
    "............###...#####.........#######............############......................",
    "............###...#####.........######.............###########....##..................",
    "............###...####..........######.............##########.....###.................",
    ".............###..####..........######.............#########.....######...............",
    ".............###..###...........######.............########......#######..............",
    ".............###..###...........######.............########..#...########.............",
    ".............###..###...........#####..............#######..#....########.............",
    "..............##..###...........#####..............######.......########..............",
    "..............##..###...........####...............#####........#######...............",
    "..............##..##............####...............####.........######................",
    "..............##..##............###................###..........####...#..............",
    "..............##..#.............###..............................##....#...............",
    "...............#...............##.....................................#...............",
    "...............#...............#......................................................",
    "...............#........................................................................",
]
LANDMASK = [row.ljust(96, ".")[:96] for row in LANDMASK]
assert len(LANDMASK) == 36 and all(len(r) == 96 for r in LANDMASK)


def draw_map(draw, x0, y0, w, h):
    """Dark-navy dotted world map inside (x0, y0, w, h)."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=NAVY2)
    cw, ch = w / 96.0, h / 36.0
    for r, row in enumerate(LANDMASK):
        for c, ch_ in enumerate(row):
            if ch_ == "#":
                cx = x0 + (c + 0.5) * cw
                cy = y0 + (r + 0.5) * ch
                draw.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6],
                             fill=LAND)


def pin(draw, x, y, n):
    """Numbered gold pin; returns the (x, y) used."""
    draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=GOLD, outline=INK, width=1)
    f = F(SANS_B, 10)
    t = str(n)
    tw = draw.textlength(t, font=f)
    draw.text((x - tw / 2, y - 7), t, font=f, fill=INK)
    return x, y


# ------------------------------------------------------- feature panels
def panel_akvan(draw, x, y, w, h):
    """Cyclone panel: dark teal, small spiral top-right, huge LANDFALL."""
    draw.rectangle([x, y, x + w, y + h], fill=TEAL)
    cx, cy = x + w * 0.80, y + 46
    for k, r in enumerate([10, 21, 32, 43, 54]):
        col = (90 + k * 22, 170 + k * 10, 170 + k * 10)
        draw.arc([cx - r, cy - r, cx + r, cy + r],
                 start=40 + k * 55, end=250 + k * 55, fill=col, width=4)
    draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(220, 240, 240))
    for i in range(8):  # rain streaks, right half only
        rx = x + w * 0.55 + i * 18
        ry = y + 8 + (i % 3) * 22
        draw.line([(rx, ry), (rx - 6, ry + 13)], fill=TEAL_LT, width=3)
    f = F(SANS_B, 44)
    draw.text((x + 14, y + h - 96), "LANDFALL", font=f, fill=(255, 255, 255))
    f2 = F(SANS_B, 15)
    draw.rectangle([x, y + h - 34, x + w, y + h], fill=GOLD)
    draw.text((x + 14, y + h - 30), "300,000 EVACUATED", font=f2, fill=INK)


def panel_kyiv(draw, x, y, w, h):
    """Kyiv panel: dark navy, one-line keyword, bridge with a blast."""
    import math
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    f = F(SANS_B, 28)
    draw.text((x + 14, y + 8), "THREE BRIDGES ", font=f,
              fill=(255, 255, 255))
    tw = draw.textlength("THREE BRIDGES ", font=f)
    draw.text((x + 14 + tw, y + 8), "HIT", font=f, fill=GOLD)
    # bridge: deck, arches, towers, river — all below the keyword
    dy = y + h - 56
    draw.line([(x + 10, dy), (x + w - 10, dy)], fill=(220, 225, 235), width=6)
    for ax in (x + 52, x + 132, x + 212):
        draw.arc([ax - 30, dy - 30, ax + 30, dy + 6], start=180, end=360,
                 fill=(220, 225, 235), width=5)
    for tx in (x + 30, x + 150, x + 250):
        draw.line([(tx, dy - 34), (tx, dy)], fill=(220, 225, 235), width=5)
    for i in range(6):
        rx = x + 20 + i * 48
        draw.line([(rx, y + h - 44), (rx + 26, y + h - 44)],
                  fill=(90, 140, 200), width=3)
    # blast on the bridge's right end
    bx, by = x + w * 0.82, dy - 12
    for r, col in [(26, (176, 60, 40)), (17, (230, 120, 40)),
                   (9, (255, 210, 63))]:
        draw.ellipse([bx - r, by - r, bx + r, by + r], fill=col)
    for i in range(8):
        a = math.radians(i * 45)
        x1 = bx + 12 * math.cos(a)
        y1 = by + 12 * math.sin(a)
        x2 = bx + 30 * math.cos(a)
        y2 = by + 30 * math.sin(a)
        draw.line([(x1, y1), (x2, y2)], fill=(255, 210, 63), width=3)
    f2 = F(SANS_B, 15)
    draw.rectangle([x, y + h - 34, x + w, y + h], fill=(176, 30, 36))
    draw.text((x + 14, y + h - 30), "3 KILLED  \u00b7  POWER AND WATER CUT",
              font=f2, fill=(255, 255, 255))


def panel_cop31(draw, x, y, w, h):
    """COP31 panel: dark green, globe, huge NO DEAL YET keyword."""
    draw.rectangle([x, y, x + w, y + h], fill=GREEN)
    cx, cy = x + w * 0.74, y + h * 0.42
    draw.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=(46, 120, 70))
    draw.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], outline=GREEN_LT,
                 width=3)
    for k, lat in enumerate([-30, 0, 30]):
        ry = 62 * abs(lat) / 90.0
        rx = 62
        draw.arc([cx - rx, cy - ry - 14, cx + rx, cy + ry + 14],
                 start=0, end=360, fill=GREEN_LT, width=2)
    draw.ellipse([cx - 52, cy - 10, cx - 18, cy + 16], fill=GREEN_LT)
    draw.ellipse([cx + 6, cy - 26, cx + 34, cy - 2], fill=GREEN_LT)
    draw.ellipse([cx - 8, cy + 14, cx + 22, cy + 40], fill=GREEN_LT)
    f = F(SANS_B, 38)
    draw.text((x + 14, y + 8), "NO DEAL", font=f, fill=(255, 255, 255))
    draw.text((x + 14, y + 50), "YET", font=f, fill=GOLD)
    f2 = F(SANS_B, 15)
    draw.rectangle([x, y + h - 34, x + w, y + h], fill=GOLD)
    draw.text((x + 14, y + h - 30), "FINAL DAY  ·  TEXT DUE AT MIDNIGHT",
              font=f2, fill=INK)


# ---------------------------------------------------------------- content
# All stories date-verified 20 November 2026 in this session. Thursday
# 19 November items sit in DATE_CHECK, never in the day's stories.
NUMBERS = [
    ("300,000", "evacuated ahead of Akvan"),
    ("\u22126.2%", "Taiwan's Taiex on Friday"),
    ("$92.22", "Brent crude a barrel"),
    ("2.2%", "Japan core inflation, October"),
    ("100,000", "youth-mobility visas a year"),
    ("60.7%", "tumours shrank in the trial"),
]

REGIONS = [
    ("ASIA", "Taiex \u22126.2%"),
    ("EUROPE", "Italy on strike"),
    ("MIDDLE EAST", "Brent $92"),
    ("AFRICA", "Senegal boat sinks"),
    ("AMERICAS", "US sanctions"),
    ("OCEANIA", "Phillips 118"),
]

FEATURES = [
    ("CYCLONE AKVAN", panel_akvan,
     "Cyclone Akvan slams India's east coast",
     "Landfall near Gopalpur at dawn, winds 70\u201380 km/h; 300,000 moved "
     "to shelters and no deaths reported \u2014 the third cyclone to "
     "threaten Odisha in 24 days.",
     "IMD \u00b7 REUTERS"),
    ("WAR IN UKRAINE", panel_kyiv,
     "Russian missiles hit three Kyiv bridges; three killed",
     "Overnight barrage knocks out power, heat and water; a day after "
     "strikes damaged Dutch and Austrian embassies, the EU summons "
     "Russia's envoy.",
     "REUTERS"),
    ("CLIMATE SUMMIT", panel_cop31,
     "COP31 reaches final day with fossil fuels erased from draft",
     "Thursday's text cut to 80 paragraphs with every fossil-fuel "
     "reference gone; \u201c35 by 35\u201d goal backed by about 75 nations; "
     "final text due at midnight.",
     "UN NEWS \u00b7 CNN"),
]

GRID = [
    # (kicker, headline, deck, source, wide, table)
    ("MARKETS", "AI sell-off sweeps Asia",
     "Taiex faces its worst week since 1990, down 17%; SoftBank \u221214.5%.",
     "REUTERS", True,
     [("TAIEX", "\u22126.2%"), ("NIKKEI", "\u22125.1%"),
      ("KOSPI", "\u22125.2%"), ("HANG SENG", "\u22121.9%")]),
    ("BRUSSELS", "UK and EU agree youth-mobility deal",
     "100,000 visas a year in a reset sealed at the summit; leaders also "
     "discuss talks with Russia on ending the war.",
     "BBC", False, None),
    ("APEC", "Xi hails \u2018full turnaround\u2019 with Australia",
     "In Shenzhen, Xi and Albanese pledge closer ties on farming, energy "
     "and AI; Albanese flies on to Beijing.",
     "REUTERS", False, None),
    ("JUSTICE", "Rohingya hail \u2018a day of justice\u2019",
     "A day after the world court found Myanmar guilty of genocide, "
     "survivors in the camps celebrate; the US says it is studying the ruling.",
     "REUTERS", False, None),
    ("ROME", "Italy stops for a general strike",
     "CGIL halts buses and metros in Rome and marches in 100 towns against "
     "the budget; trains and flights are spared on Friday.",
     "ANSA", False, None),
    ("SCIENCE", "Cancer pill clears tumours in 1 in 12",
     "Daraxonrasib with chemo shrank tumours in 60.7% of patients in an "
     "early trial presented in Barcelona; 76.6% alive after a year.",
     "EORTC", False, None),
    ("CRICKET", "Phillips completes a century treble",
     "118 in Wellington \u2014 the first batter to hit Test, ODI and T20I "
     "hundreds against India in one year. NZ 368; India 159\u20131.",
     "REUTERS", False, None),
    ("ECONOMY", "Japan inflation hits a 2026 high",
     "Core prices up 2.2% in October, above the Bank of Japan's target; "
     "China holds loan rates for an 18th month.",
     "REUTERS", False, None),
    ("ENERGY", "Oil climbs as Hormuz tankers hit mines",
     "Brent $92.22 after two tankers strike mines in the strait and Houthi "
     "attacks on Riyadh; still set for a third weekly fall.",
     "REUTERS", False, None),
]

BRIEFS = [
    ("IRAQ", "troops enter the Kataib Hezbollah stronghold under a deal"),
    ("F1", "Russell tops a rain-hit Las Vegas FP2 in 1:47.272 after FP1 is washed out"),
    ("GENOA", "airport halts flights after unidentified drones are spotted"),
    ("UKRAINE", "Britain pledges 1,000+ drones for Kyiv in a \u00a3260m package"),
    ("SANCTIONS", "US targets the Comancheros gang and Italy's 'Ndrangheta"),
    ("ANTHROPIC", "shares slip 4.7% after hours after Thursday's record debut"),
    ("SENEGAL", "four bodies recovered after a migrant boat capsizes off Yenne; dozens missing"),
    ("MALAWI", "fuel queues stretch overnight; petrol $3.24 a litre, Africa's dearest"),
    ("ARGENTINA", "Senate backs a disability framework unanimously, 71\u20130"),
    ("POLAND", "probes unknown objects in its skies; air-threat warning lifted"),
    ("IRAN WAR", "has cost the US $48.3bn, the Pentagon says"),
    ("RIYADH", "Saudi defences shoot down two Houthi drones"),
    ("LEBANON", "Israeli strike hits a Hezbollah missile site in the east"),
    ("TBILISI", "six killed in a gas blast at an apartment block"),
    ("NEW CALEDONIA", "5.6-magnitude quake strikes off the islands"),
    ("FRANCE", "one dead and 15 hurt in a fire at an 18-storey block"),
    ("PARIS", "Harris meets Macron in a courtesy call"),
    ("UNITED NATIONS", "ninth ballot due in the race to lead the UN"),
    ("VMWARE", "Broadcom patches a critical flaw in vCenter"),
    ("CINCINNATI", "Fiona the hippo dies after swallowing a hat"),
]

DATE_CHECK = [
    "Anthropic debuts on Nasdaq, +17% \u2014 $83 to $97.17 in a record $81.3bn IPO",
    "Trump, Xi and Putin meet in Shenzhen; a peace declaration follows",
    "Bukele files for a third term as El Salvador's president",
    "World court: Myanmar guilty of Rohingya genocide, 9\u20136",
    "US\u2013Venezuela deal signed",
    "COP31 draft drops every fossil-fuel reference",
    "Senate rejects an Iran war-powers bid, 51\u201348",
    "Trump pardons Pete Rose posthumously",
    "Strikes damage Dutch and Austrian embassies in Kyiv",
    "Meta rethinks its 2030 net-zero goal as AI emissions jump 45%",
]

# (map x, map y, key label) — pixel coords inside the map panel.
PINS = [
    (360, 732, "Gopalpur \u2014 Cyclone Akvan landfall"),
    (297, 699, "Kyiv \u2014 three bridges hit"),
    (302, 716, "Antalya \u2014 COP31 final day"),
    (422, 726, "Taipei \u2014 Taiex \u22126.2%"),
    (438, 714, "Tokyo \u2014 Nikkei \u22125.1%"),
    (412, 712, "Seoul \u2014 Kospi \u22125.2%"),
    (252, 694, "Brussels \u2014 UK\u2013EU youth deal"),
    (398, 729, "Shenzhen \u2014 Xi meets Albanese"),
    (286, 710, "Rome \u2014 general strike"),
    (258, 714, "Barcelona \u2014 cancer pill trial"),
    (477, 797, "Wellington \u2014 Phillips 118"),
    (330, 724, "Strait of Hormuz \u2014 tankers hit mines"),
    (378, 730, "Cox's Bazar \u2014 Rohingya hail ruling"),
]


# ---------------------------------------------------------------- layout
def masthead(draw):
    f_title = F(SERIF_B, 54)
    draw.text((24, 12), "THE WORLD TODAY", font=f_title, fill=INK)
    f_date = F(SANS_B, 16)
    f_sub = F(SANS, 11)
    rx = 1024 - 24
    draw.text((rx - draw.textlength("FRIDAY 20 NOVEMBER 2026", font=f_date),
               16), "FRIDAY 20 NOVEMBER 2026", font=f_date, fill=RED)
    draw.text((rx - draw.textlength("THE DAY IN ONE PAGE", font=f_sub), 38),
              "THE DAY IN ONE PAGE", font=f_sub, fill=GREY)
    draw.text((rx - draw.textlength("Reuters \u00b7 BBC \u00b7 AP \u00b7 UN News",
                                    font=f_sub), 54),
              "Reuters \u00b7 BBC \u00b7 AP \u00b7 UN News", font=f_sub,
              fill=GREY)
    hline(draw, 24, 1000, 76, width=3)
    hline(draw, 24, 1000, 80, width=1)


def numbers_strip(draw):
    y0, y1 = 86, 128
    cw = 976 / 6
    f_num = F(SANS_B, 25)
    f_lab = F(SANS, 10)
    for i, (num, lab) in enumerate(NUMBERS):
        x = 24 + i * cw
        if i:
            draw.line([(x - 5, y0 + 4), (x - 5, y1 - 4)], fill=FAINT, width=1)
        draw.text((x, y0), num, font=f_num, fill=RED)
        for j, ln in enumerate(wrap(lab, f_lab, cw - 12, draw)):
            draw.text((x, y0 + 27 + j * 12), ln, font=f_lab, fill=GREY)
    hline(draw, 24, 1000, 136, width=1)


def region_strip(draw):
    y = 142
    cw = 976 / 6
    f = F(SANS, 11)
    fb = F(SANS_B, 11)
    for i, (reg, txt) in enumerate(REGIONS):
        x = 24 + i * cw
        draw.text((x, y), reg, font=fb, fill=INK)
        tx = x + draw.textlength(reg + "  ", font=fb)
        draw.text((tx, y), txt, font=f, fill=GREY)
    hline(draw, 24, 1000, 162, width=1)


def features(draw):
    y0 = 170
    colw = 317
    xs = [24, 353, 682]
    panel_h = 140
    for (kick, panel_fn, head, deck, src), x in zip(FEATURES, xs):
        panel_fn(draw, x, y0, colw, panel_h)
        yy = y0 + panel_h + 8
        yy = kicker(draw, x, yy, kick, size=11)
        f_head = F(SERIF_B, 22)
        lines = wrap(head, f_head, colw, draw)[:2]
        yy = text_block(draw, x, yy, lines, f_head, leading=24)
        f_deck = F(SERIF, 12)
        lines = wrap(deck, f_deck, colw, draw)[:3]
        yy = text_block(draw, x, yy + 2, lines, f_deck, leading=14)
        f_src = F(SANS, 9)
        draw.text((x, y0 + 256), "SOURCE: " + src, font=f_src, fill=GREY)
    hline(draw, 24, 1000, 434, width=1)


def grid(draw):
    y0 = 442
    colw = 187
    gap = 10
    xs = [24 + i * (colw + gap) for i in range(5)]
    row_h = 96
    f_kick = F(SANS_B, 10)
    f_head = F(SERIF_B, 15)
    f_deck = F(SERIF, 11)
    f_src = F(SANS, 8)

    def cell(x, y, w, kick, head, deck, src, table=None):
        draw.text((x, y), kick, font=f_kick, fill=RED)
        yy = y + 14
        lines = wrap(head, f_head, w, draw)[:2]
        yy = text_block(draw, x, yy, lines, f_head, leading=17)
        if table:
            f_tab = F(SANS_B, 11)
            f_tv = F(SANS_B, 11)
            ty = yy + 2
            for j, (name, val) in enumerate(table):
                tx = x + j * (w // 4)
                draw.text((tx, ty), name, font=F(SANS, 9), fill=GREY)
                draw.text((tx, ty + 11), val, font=f_tv, fill=RED)
            yy = ty + 26
            max_deck = 1
        else:
            max_deck = 3
        lines = wrap(deck, f_deck, w, draw)[:max_deck]
        yy = text_block(draw, x, yy + 1, lines, f_deck, leading=13)
        draw.text((x, y + row_h - 10), "SOURCE: " + src, font=f_src,
                  fill=GREY)

    # row 1: markets wide (cols 1-2) + 3 singles
    wide_w = colw * 2 + gap
    cell(xs[0], y0, wide_w, *GRID[0][:4], table=GRID[0][5])
    cell(xs[2], y0, colw, *GRID[1][:4])
    cell(xs[3], y0, colw, *GRID[2][:4])
    cell(xs[4], y0, colw, *GRID[3][:4])
    # row 2: 5 singles
    y1 = y0 + row_h + 8
    for i, g in enumerate(GRID[4:]):
        cell(xs[i], y1, colw, *g[:4])
    hline(draw, 24, 1000, y1 + row_h + 6, width=1)


def map_and_key(draw):
    y0 = 654
    draw.rectangle([24, y0, 494, 820], outline=INK, width=1)
    draw.rectangle([506, y0, 1000, 820], outline=INK, width=1)
    f_title = F(SANS_B, 12)
    draw.text((34, y0 + 6), "WHERE IT HAPPENED", font=f_title, fill=INK)
    draw.text((520, y0 + 6), "PIN KEY", font=f_title, fill=INK)
    draw_map(draw, 34, 672, 450, 140)
    for i, (px, py, _label) in enumerate(PINS, start=1):
        pin(draw, px, py, i)
    f_key = F(SANS, 10)
    f_num = F(SANS_B, 10)
    col_x = [520, 762]
    for i, (_px, _py, label) in enumerate(PINS, start=1):
        col = 0 if i <= 7 else 1
        row = (i - 1) if i <= 7 else (i - 8)
        x = col_x[col]
        y = 672 + row * 21
        draw.rectangle([x, y + 1, x + 15, y + 14], fill=GOLD, outline=INK,
                       width=1)
        t = str(i)
        draw.text((x + 8 - draw.textlength(t, font=f_num) / 2, y + 2), t,
                  font=f_num, fill=INK)
        draw.text((x + 21, y + 2), label, font=f_key, fill=INK)


def briefs(draw):
    y0 = 826
    f_title = F(SANS_B, 11)
    draw.text((24, y0), "THE REST OF THE DAY", font=f_title, fill=INK)
    hline(draw, 24, 1000, y0 + 15, width=1)
    f_lead = F(SANS_B, 10)
    f_rest = F(SANS, 10)
    cols = [(24, 470), (514, 470)]
    for ci, (cx, cw) in enumerate(cols):
        items = BRIEFS[ci * 10:(ci + 1) * 10]
        y = y0 + 21
        for lead, rest in items:
            draw.text((cx, y), lead, font=f_lead, fill=RED)
            lx = cx + draw.textlength(lead + "  ", font=f_lead)
            line = rest
            # single line, clipped to the column width
            while (draw.textlength(line, font=f_rest) > cw - (lx - cx)
                   and len(line) > 10):
                line = line.rsplit(" ", 1)[0] + "\u2026"
            draw.text((lx, y), line, font=f_rest, fill=INK)
            y += 10.0
    return y0 + 21 + 10 * 10.0


def date_check(draw):
    y0 = 950
    draw.rectangle([24, y0, 1000, 1018], outline=RED, width=1)
    draw.rectangle([24, y0, 1000, y0 + 17], fill=RED)
    f_title = F(SANS_B, 11)
    draw.text((32, y0 + 3),
              "DATE CHECK \u2014 THESE HAPPENED ON THURSDAY 19 NOVEMBER, NOT TODAY",
              font=f_title, fill=(255, 255, 255))
    f_item = F(SANS, 9)
    for i, item in enumerate(DATE_CHECK):
        col = 0 if i < 5 else 1
        row = i if i < 5 else i - 5
        x = 32 + col * 490
        y = y0 + 21 + row * 9.5
        draw.text((x, y), "\u2022  " + item, font=f_item, fill=INK)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    masthead(draw)
    numbers_strip(draw)
    region_strip(draw)
    features(draw)
    grid(draw)
    map_and_key(draw)
    briefs(draw)
    date_check(draw)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    return OUT


def main():
    path = build()
    size = os.path.getsize(path)
    im = Image.open(path)
    print("wrote", path)
    print("size_bytes", size, "limit", 1048576, "ok", size <= 1048576)
    print("dimensions", im.size)
    print("features", len(FEATURES))
    print("grid_stories", len(GRID))
    print("numbers", len(NUMBERS))
    print("regions", len(REGIONS))
    print("briefs", len(BRIEFS))
    print("date_check_items", len(DATE_CHECK))
    print("pins", len(PINS))
    print("stories_total", len(FEATURES) + len(GRID) + len(BRIEFS))


if __name__ == "__main__":
    main()
