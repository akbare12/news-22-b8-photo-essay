#!/usr/bin/env python3
"""Draw THE WORLD TODAY — a photo-essay front page for 22 Nov 2026.

Everything is drawn with PIL primitives. Layout (1024x1024):
masthead / numbers strip / 3 hero photo panels / 6-frame photo strip /
map + pin key / story grid 10-32 / NOT YET strip / date-check footer.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (26, 26, 26)
NAVY = (16, 34, 64)
NAVY2 = (24, 48, 88)
RED = (178, 34, 34)
DARKRED = (122, 18, 18)
GOLD = (201, 162, 39)
GREEN = (34, 120, 60)
AMBER = (176, 124, 18)
BLUE = (40, 90, 160)
GREY = (90, 86, 78)
LIGHTBLUE = (196, 222, 235)
TAN = (222, 198, 150)

FD = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FD + name, size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def trunc(draw, text, fnt, max_w):
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "...", font=fnt) > max_w:
        text = text[:-1]
    return text + "..."


def badge(d, x, y, label, color):
    f = SANS_B(10)
    w = d.textlength(label, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 15], radius=3, fill=color)
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def flame(d, cx, cy, s):
    # layered flame: outer orange, mid yellow, core pale
    d.polygon([(cx - 0.55 * s, cy), (cx - 0.28 * s, cy - 0.75 * s),
               (cx - 0.05 * s, cy - 0.35 * s), (cx + 0.18 * s, cy - 1.0 * s),
               (cx + 0.42 * s, cy - 0.45 * s), (cx + 0.55 * s, cy)],
              fill=(232, 96, 20))
    d.polygon([(cx - 0.32 * s, cy), (cx - 0.16 * s, cy - 0.5 * s),
               (cx + 0.02 * s, cy - 0.22 * s), (cx + 0.14 * s, cy - 0.62 * s),
               (cx + 0.30 * s, cy - 0.25 * s), (cx + 0.32 * s, cy)],
              fill=(246, 196, 40))
    d.polygon([(cx - 0.14 * s, cy), (cx - 0.06 * s, cy - 0.28 * s),
               (cx + 0.08 * s, cy - 0.34 * s), (cx + 0.14 * s, cy)],
              fill=(255, 240, 170))


def smoke(d, cx, cy, r, color=(120, 118, 112)):
    for dx, dy, rr in [(-r, 0, r), (0, -r * 0.7, r * 1.1), (r, -r * 0.2, r * 0.9),
                       (0, -r * 1.5, r * 0.8)]:
        d.ellipse([cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr],
                  fill=color)


def star(d, cx, cy, r, color, n=5):
    import math
    pts = []
    for i in range(2 * n):
        ang = -math.pi / 2 + i * math.pi / n
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=color)


def draw_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 42, 74))
    # sun / haze
    d.ellipse([x + w - 52, y + 10, x + w - 16, y + 46], fill=(240, 200, 90))
    # sea
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(28, 78, 128))
    for i in range(5):
        wx = x + 12 + i * 62
        d.arc([wx, y + h * 0.66, wx + 44, y + h * 0.82], 0, 180,
              fill=(160, 200, 235), width=3)
    # tanker hull
    hx, hy = x + 30, y + h * 0.52
    d.polygon([(hx, hy), (hx + w - 80, hy), (hx + w - 60, hy + 34),
               (hx + 8, hy + 34)], fill=(214, 72, 20))
    d.rectangle([hx + 18, hy - 26, hx + 52, hy], fill=(240, 240, 235))
    d.rectangle([hx + 60, hy - 18, hx + 96, hy], fill=(200, 200, 195))
    # flames on deck + smoke
    flame(d, hx + 150, hy + 2, 34)
    flame(d, hx + 205, hy + 2, 26)
    smoke(d, hx + 178, hy - 30, 11)
    # mine in water
    mx, my = x + w - 48, y + h - 26
    d.ellipse([mx - 11, my - 11, mx + 11, my + 11], fill=(20, 20, 20))
    for dx, dy in [(-13, 0), (13, 0), (0, -13), (0, 13), (-9, -9), (9, -9),
                    (-9, 9), (9, 9)]:
        d.line([mx, my, mx + dx, my + dy], fill=(20, 20, 20), width=3)


def draw_globe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(122, 18, 18))
    cx, cy, r = x + w / 2, y + h / 2 + 6, 58
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(168, 208, 226))
    # land blobs
    d.ellipse([cx - 52, cy - 38, cx - 6, cy - 2], fill=(96, 160, 92))
    d.ellipse([cx + 2, cy + 8, cx + 48, cy + 44], fill=(96, 160, 92))
    d.ellipse([cx + 12, cy - 44, cx + 44, cy - 14], fill=(120, 175, 100))
    d.ellipse([cx - 44, cy + 18, cx - 12, cy + 46], fill=(120, 175, 100))
    # crack
    pts = [(cx - 30, cy - 62), (cx - 12, cy - 34), (cx - 26, cy - 8),
           (cx + 2, cy + 14), (cx - 10, cy + 38), (cx + 14, cy + 62)]
    d.line(pts, fill=(20, 20, 20), width=5, joint="curve")
    # small flags / sparks
    star(d, x + 26, y + 22, 7, GOLD)
    star(d, x + w - 26, y + h - 24, 7, GOLD)


def draw_capitol(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 34, 64))
    for sx, sy in [(x + 24, y + 20), (x + 52, y + 44), (x + w - 52, y + 26),
                    (x + w - 24, y + 52), (x + w // 2, y + 14)]:
        star(d, sx, sy, 6, GOLD)
    cx = x + w / 2
    base = y + h - 8
    # dome
    d.pieslice([cx - 62, base - 88, cx + 62, base - 8], 180, 360,
               fill=(245, 245, 240))
    d.rectangle([cx - 6, base - 104, cx + 6, base - 84], fill=(245, 245, 240))
    d.ellipse([cx - 8, base - 104, cx + 8, base - 92], fill=GOLD)
    # drum + columns
    d.rectangle([cx - 58, base - 52, cx + 58, base], fill=(235, 235, 230))
    for i in range(7):
        colx = cx - 50 + i * 16
        d.rectangle([colx, base - 46, colx + 8, base - 6], fill=(16, 34, 64))
    d.rectangle([cx - 70, base - 58, cx + 70, base - 50], fill=(245, 245, 240))
    # steps
    d.rectangle([x + 40, base - 2, x + w - 40, base + 2], fill=(200, 200, 195))


def thumb_merkury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 52, 84))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(40, 96, 148))
    d.polygon([(x + 22, y + h * 0.6), (x + w - 40, y + h * 0.6),
               (x + w - 28, y + h * 0.78), (x + 30, y + h * 0.78)],
              fill=(150, 150, 148))
    d.rectangle([x + 34, y + h * 0.42, x + 56, y + h * 0.6], fill=(210, 210, 205))
    flame(d, x + w - 46, y + h * 0.62, 26)
    smoke(d, x + w - 46, y + h * 0.3, 10)
    d.ellipse([x + 14, y + 10, x + 26, y + 18], fill=(230, 230, 230))


def thumb_khartoum(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 214, 186))
    d.rectangle([x + 14, y + h * 0.42, x + 62, y + h], fill=(150, 120, 92))
    d.rectangle([x + 66, y + h * 0.3, x + 118, y + h], fill=(170, 140, 108))
    d.rectangle([x + 122, y + h * 0.52, x + w - 12, y + h], fill=(140, 110, 84))
    smoke(d, x + 92, y + h * 0.22, 13)
    flame(d, x + 92, y + h * 0.32, 22)
    d.ellipse([x + w - 26, y + 8, x + w - 12, y + 18], fill=(60, 60, 60))


def thumb_banten(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 40, 44))
    d.rectangle([x + 12, y + h * 0.5, x + w - 12, y + h], fill=(196, 120, 60))
    for i in range(4):
        bx = x + 22 + i * 34
        d.polygon([(bx, y + h * 0.5), (bx + 17, y + h * 0.34),
                   (bx + 34, y + h * 0.5)], fill=(120, 70, 40))
    flame(d, x + w / 2, y + h * 0.52, 34)
    smoke(d, x + w / 2, y + h * 0.16, 13)


def thumb_patriot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 48, 88))
    cx, cy = x + w / 2, y + h / 2 + 6
    d.polygon([(cx, cy - 40), (cx + 42, cy - 22), (cx + 42, cy + 6),
               (cx, cy + 42), (cx - 42, cy + 6), (cx - 42, cy - 22)],
              fill=(240, 240, 235))
    d.polygon([(cx, cy - 30), (cx + 30, cy - 16), (cx + 30, cy + 4),
               (cx, cy + 30), (cx - 30, cy + 4), (cx - 30, cy - 16)],
              fill=(40, 90, 160))
    d.line([x + 16, y + 18, cx - 6, cy - 30], fill=(246, 196, 40), width=3)
    d.line([x + w - 16, y + 14, cx + 8, cy - 28], fill=(246, 196, 40), width=3)
    star(d, cx - 24, cy - 34, 5, GOLD)
    star(d, cx + 26, cy - 32, 5, GOLD)


def thumb_missile(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 30, 34))
    d.pieslice([x + 18, y + 14, x + w - 18, y + 120], 180, 360, fill=(70, 70, 78))
    d.rectangle([x + 18, y + 66, x + w - 18, y + h], fill=(58, 58, 66))
    mx = x + w / 2
    d.polygon([(mx - 9, y + h - 12), (mx - 9, y + 34), (mx, y + 18),
               (mx + 9, y + 34), (mx + 9, y + h - 12)], fill=(200, 200, 196))
    d.polygon([(mx - 9, y + 34), (mx, y + 18), (mx + 9, y + 34)],
              fill=(178, 34, 34))
    for fy in (52, 66, 80):
        d.ellipse([x + 26, fy, x + 34, fy + 6], fill=(246, 196, 40))
        d.ellipse([x + w - 34, fy, x + w - 26, fy + 6], fill=(246, 196, 40))


def thumb_nvidia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 240, 234))
    # grid
    for gx in range(x + 12, x + w - 8, 26):
        d.line([gx, y + 10, gx, y + h - 14], fill=(215, 218, 210), width=1)
    for gy in range(y + 12, y + h - 8, 20):
        d.line([x + 10, gy, x + w - 10, gy], fill=(215, 218, 210), width=1)
    pts = [(x + 14, y + h - 22), (x + 44, y + h - 44), (x + 66, y + h - 36),
           (x + 96, y + h - 62), (x + 122, y + h - 48), (x + w - 16, y + 16)]
    d.line(pts, fill=(34, 120, 60), width=5, joint="curve")
    d.polygon([(x + w - 30, y + 10), (x + w - 10, y + 10), (x + w - 16, y + 30)],
              fill=(34, 120, 60))
    d.rectangle([x + 12, y + 12, x + 46, y + 30], fill=(16, 34, 64))
    d.text((x + 17, y + 16), "+33%", font=SANS_B(11), fill=(255, 255, 255))


def draw_map(d, x, y, w, h, pins):
    d.rectangle([x, y, x + w, y + h], fill=LIGHTBLUE)
    d.rectangle([x, y, x + w, y + h], outline=GREY, width=1)
    # rough continents (tan polygons, schematic)
    polys = [
        [(14, 26), (52, 8), (96, 14), (104, 40), (78, 58), (58, 78), (30, 66),
         (12, 48)],  # N America
        [(84, 78), (108, 74), (116, 96), (100, 118), (86, 100)],  # S America
        [(196, 22), (228, 12), (252, 26), (240, 44), (214, 46), (198, 36)],
        # Europe
        [(206, 48), (248, 44), (268, 66), (246, 92), (222, 88), (206, 68)],
        # Africa
        [(272, 30), (330, 16), (392, 26), (420, 44), (380, 62), (330, 76),
         (292, 60)],  # Asia
        [(400, 108), (436, 102), (444, 118), (414, 124)],  # SE Asia / Oceania
    ]
    for p in polys:
        d.polygon([(x + px, y + py) for px, py in p], fill=TAN,
                  outline=(180, 158, 110))
    # grid lines
    for gx in range(0, w, 60):
        d.line([x + gx, y, x + gx, y + h], fill=(170, 200, 215), width=1)
    for gy in range(0, h, 30):
        d.line([x, y + gy, x + w, y + gy], fill=(170, 200, 215), width=1)
    for num, px, py in pins:
        d.ellipse([x + px - 9, y + py - 9, x + px + 9, y + py + 9],
                  fill=RED, outline=(255, 255, 255), width=2)
        f = SANS_B(10)
        tw = d.textlength(str(num), font=f)
        d.text((x + px - tw / 2, y + py - 7), str(num), font=f,
               fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- top red rule + masthead ---
    d.rectangle([0, 0, W, 8], fill=RED)
    d.text((16, 12), "THE WORLD TODAY", font=SERIF_B(46), fill=INK)
    d.text((1024 - 16 - d.textlength("SUNDAY 22 NOVEMBER 2026",
                                    font=SANS_B(20)), 24),
           "SUNDAY 22 NOVEMBER 2026", font=SANS_B(20), fill=RED)
    d.line([16, 66, W - 16, 66], fill=RED, width=3)
    d.text((16, 71), "32 STORIES  ·  IN PICTURES  —  EVERY ITEM FIRST REPORTED 22 NOV",
           font=SANS_B(13), fill=INK)
    lx = W - 16
    for label, color in [("ONGOING", BLUE), ("CLAIM", AMBER), ("REPORTED", GREEN)]:
        f = SANS_B(10)
        w = d.textlength(label, font=f) + 10
        lx -= w + 6
        d.rounded_rectangle([lx, 71, lx + w, 86], radius=3, fill=color)
        d.text((lx + 5, 73), label, font=f, fill=(255, 255, 255))
    d.text((lx - 130, 73), "HOW WE KNOW:", font=SANS_B(10), fill=GREY)

    # --- numbers strip ---
    d.rectangle([16, 94, W - 16, 126], fill=NAVY)
    nums = [("258", "House seats"), ("2", "tankers hit"), ("194", "COP31 parties"),
            ("330", "votes in NC"), ("36", "missing in Banten"),
            ("1,661", "Gaza toll")]
    seg = (W - 32) / 6
    for i, (n, lab) in enumerate(nums):
        x0 = 16 + i * seg
        d.text((x0 + 14, 99), n, font=SERIF_B(22), fill=GOLD)
        d.text((x0 + 14 + d.textlength(n, font=SERIF_B(22)) + 8, 106), lab,
               font=SANS(12), fill=(235, 235, 230))

    # --- hero photo panels ---
    heroes = [
        ("CONFLICT · STRAIT OF HORMUZ", "17:13 UTC", "2 TANKERS HIT",
         "Two supertankers hit mines east of the Strait, north of Ghanam "
         "Island; both on fire.", "REPORTED", "Iran navy · AP", draw_tanker),
        ("CLIMATE · ANTALYA", "12:00 UTC", "NO DEAL",
         "COP31 collapses; EU + ~130 parties reject a text with no fossil "
         "fuels. Longest COP ever.", "REPORTED", "CNN · Reuters", draw_globe),
        ("POLITICS · WASHINGTON", "EVENING", "258",
         "Dems win House, largest majority since 1992; Hubbard beats Foxx "
         "by 330 in NC recount.", "REPORTED", "AP · Reuters", draw_capitol),
    ]
    hy, hh, hw = 134, 236, 322
    for i, (kick, when, head, body, tag, src, fn) in enumerate(heroes):
        x = 16 + i * (hw + 8)
        fn(d, x, hy, hw, 116)
        d.rectangle([x, hy + 116, x + hw, hy + hh], fill=(255, 255, 255),
                    outline=GREY, width=1)
        d.text((x + 10, hy + 122), kick, font=SANS_B(11), fill=RED)
        d.text((x + hw - 10 - d.textlength(when, font=SANS_B(11)), hy + 122),
               when, font=SANS_B(11), fill=GREY)
        d.text((x + 10, hy + 140), head, font=SERIF_B(28), fill=INK)
        lines = wrap(d, body, SANS(11), hw - 20)
        yy = hy + 176
        for ln in lines[:2]:
            d.text((x + 10, yy), ln, font=SANS(11), fill=(50, 50, 50))
            yy += 13
        badge(d, x + 10, hy + hh - 24, tag, GREEN)
        d.text((x + 10 + 78, hy + hh - 22), src, font=SANS(11), fill=GREY)

    # --- photo strip: six frames ---
    d.text((16, 378), "IN PICTURES — THE DAY IN SIX FRAMES",
           font=SANS_B(13), fill=INK)
    d.text((W - 16 - d.textlength("EVERY FRAME A STORY · CAPTIONS BELOW",
                                  font=SANS_B(10)), 380),
           "EVERY FRAME A STORY · CAPTIONS BELOW", font=SANS_B(10), fill=GREY)
    frames = [
        ("04", "Merkury hit at Benghazi", "CLAIM", "France 24", thumb_merkury),
        ("05", "Khartoum drones kill 4, UN hit", "CLAIM", "AP", thumb_khartoum),
        ("06", "Banten factory fire — 3 dead, 36 missing", "", "BBC", thumb_banten),
        ("07", "Zelenskyy pleads for Patriots", "", "BBC", thumb_patriot),
        ("08", "Iran shows underground missile city", "", "IRGC media",
         thumb_missile),
        ("09", "Nvidia: Huang back, shares +33%", "", "One Turn", thumb_nvidia),
    ]
    fy, fh, fw = 398, 96, 160
    for i, (num, cap, tag, src, fn) in enumerate(frames):
        x = 16 + i * (fw + 8)
        fn(d, x, fy, fw, fh)
        d.rectangle([x, fy, x + fw, fy + fh], outline=GREY, width=1)
        d.text((x, fy + fh + 4), num, font=SANS_B(11), fill=RED)
        lines = wrap(d, cap, SANS_B(11), fw - 22)
        yy = fy + fh + 4
        for ln in lines[:2]:
            d.text((x + 22, yy), ln, font=SANS_B(11), fill=INK)
            yy += 13
        tagline = (tag + " · " if tag else "") + src
        d.text((x, fy + fh + 32), tagline, font=SANS(10), fill=GREY)

    # --- map band ---
    d.text((16, 540), "WHERE IT HAPPENED — EVERY HERO PINNED",
           font=SANS_B(13), fill=INK)
    d.text((W - 16 - d.textlength("ALL TIMES UTC", font=SANS_B(10)), 542),
           "ALL TIMES UTC", font=SANS_B(10), fill=GREY)
    mapx, mapy, mapw, maph = 16, 560, 600, 118
    pins = [(1, 300, 66), (2, 252, 34), (3, 62, 34), (4, 262, 58),
            (5, 258, 76), (6, 212, 28), (7, 392, 88), (8, 316, 88)]
    draw_map(d, mapx, mapy, mapw, maph, pins)
    kx = 632
    d.text((kx, 560), "PIN KEY", font=SANS_B(12), fill=INK)
    key = [("1", "Hormuz — 2 tankers hit mines, 17:13"),
           ("2", "Antalya — COP31 collapses, no deal"),
           ("3", "Washington — Dems reach 258"),
           ("4", "Benghazi — Russian ship hit, depot blast"),
           ("5", "Khartoum — drones kill 4, UN hit"),
           ("6", "Kyiv — Dymer flats hit"),
           ("7", "Banten — factory fire, 36 missing"),
           ("8", "Gaza — toll 1,661 since Oct 2025")]
    for i, (n, t) in enumerate(key):
        yy = 580 + i * 12
        d.text((kx, yy), n, font=SANS_B(10), fill=RED)
        d.text((kx + 14, yy), t, font=SANS(10), fill=(50, 50, 50))

    # --- story grid 10-32 ---
    d.text((16, 686), "THE DAY IN BRIEF — STORIES 10–32",
           font=SANS_B(13), fill=INK)
    d.line([16, 704, W - 16, 704], fill=INK, width=2)
    grid = [
        ("10", "Saudi stops Houthi attack", "CLAIM", "Reuters"),
        ("11", "Bahrain blames Iran", "", "France 24"),
        ("12", "UAE condemns Bahrain strike", "", "WAM"),
        ("13", "Europe protests, day 3", "", "AP"),
        ("14", "Settlers burn West Bank cars", "", "Guardian"),
        ("15", "Benghazi depot blast", "", "Local auth."),
        ("16", "Unity talks stall", "", "Israeli media"),
        ("17", "Finland: war spills over", "", "Finnish govt"),
        ("18", "Gaza aid van strike — WCK: not our team", "", "WCK"),
        ("19", "\u201cIran war was avoidable\u201d", "", "MED Dialogues"),
        ("20", "Fidan: Israel may use Druze", "CLAIM", "Anadolu"),
        ("21", "Fidan: war fallout hits markets", "", "Anadolu"),
        ("22", "Aoun: Israel must leave", "", "Al Jazeera"),
        ("23", "Gaza: 350,000 homeless", "", "Al Jazeera"),
        ("24", "Pezeshkian: silent war", "", "IRNA"),
        ("25", "Settlers attack homes in Hebron", "", "WAFA"),
        ("26", "Gaza homes blocked", "CLAIM", "Anadolu"),
        ("27", "Germany urged to arrest soldier", "", "HRF"),
        ("28", "Fred Nile dies at 92", "", "Guardian"),
        ("29", "Gamer rescues missing girl", "", "FBI"),
        ("30", "Gaza toll 1,661", "", "Gaza health min."),
        ("31", "Ex-police chief found dead", "", "ANSA"),
        ("32", "Trump, Xi, Putin joint declaration", "", "Russell Record"),
    ]
    colw = (W - 32 - 24) / 2
    for i, (num, head, tag, src) in enumerate(grid):
        col = i % 2
        row = i // 2
        x0 = 16 + col * (colw + 24)
        y0 = 712 + row * 19
        d.text((x0, y0), num, font=SANS_B(11), fill=RED)
        max_head = colw - 34 - (d.textlength(tag, font=SANS_B(9)) + 8
                                if tag else 0) - d.textlength(src, font=SANS(9)) - 8
        htext = trunc(d, head, SANS_B(11), max_head)
        d.text((x0 + 26, y0), htext, font=SANS_B(11), fill=INK)
        rx = x0 + colw
        d.text((rx - d.textlength(src, font=SANS(9)), y0 + 1), src,
               font=SANS(9), fill=GREY)
        if tag:
            tw = d.textlength(tag, font=SANS_B(9)) + 8
            tx = rx - d.textlength(src, font=SANS(9)) - 8 - tw
            d.rounded_rectangle([tx, y0 + 1, tx + tw, y0 + 13], radius=2,
                                fill=AMBER)
            d.text((tx + 4, y0 + 2), tag, font=SANS_B(9), fill=(255, 255, 255))

    # --- NOT YET strip ---
    d.rectangle([16, 948, W - 16, 970], fill=(252, 232, 170),
                outline=GOLD, width=1)
    d.text((24, 953),
           "NOT YET — DO NOT READ AS DONE:  4 House races uncalled  ·  "
           "COP32 venue not set  ·  Gaza ceasefire talks: no deal announced",
           font=SANS_B(11), fill=(90, 60, 0))

    # --- footer ---
    d.text((16, 976),
           "DATE CHECK — Every story above was first reported on 22 Nov, unless its "
           "kicker says otherwise.",
           font=SANS(10), fill=GREY)
    d.text((16, 988),
           "EXCLUDED: El Chapo Isidro captured 20 Nov · BepiColombo Mercury orbit "
           "21 Nov · ICJ Myanmar ruling 19 Nov · Wall St rout 20 Nov · FBI NCIC "
           "hack first reported 21 Nov.",
           font=SANS(10), fill=GREY)
    d.text((16, 1000),
           "LEGEND: REPORTED = confirmed by 2+ sources · CLAIM = one side alleges, "
           "unverified · ONGOING = still developing.",
           font=SANS(10), fill=GREY)
    d.text((16, 1012),
           "SOURCES: AP · Reuters · BBC · CNN · France 24 · Al Jazeera · Guardian · "
           "IRNA · Anadolu · WAFA · HRF · WCK · FBI · ANSA · Euronews · One Turn · "
           "dailysummaryof, 22 Nov 2026.",
           font=SANS(10), fill=GREY)

    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    img.save(path, "PNG")
    print("wrote", path, img.size)


if __name__ == "__main__":
    main()
