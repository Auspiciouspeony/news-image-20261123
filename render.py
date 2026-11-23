#!/usr/bin/env python3
"""Render the 23 November 2026 world-news front page (1024x1024 PNG).

Deterministic: no clock, no randomness, no network. Reads nothing but
system fonts; writes assets/entry.png next to this script. Run twice and
the bytes are identical.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

PAPER = (247, 242, 231)
INK = (20, 33, 61)
RED = (180, 35, 24)
GOLD = (176, 138, 30)
TEAL = (14, 124, 123)
SLATE = (90, 100, 114)
LIGHT = (233, 226, 210)
WHITE = (255, 255, 255)
BLUE = (38, 84, 124)

W = H = 1024


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(draw, text, fnt, max_w, suffix="..."):
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + suffix, font=fnt) > max_w:
        text = text[:-1]
    return text + suffix


def draw_globe(draw, cx, cy, r):
    """Stylised globe with a red crack: the climate talks breaking apart.
    Drawn on its own layer and masked to a circle so the meridian arcs
    never spill past the globe's edge."""
    layer = Image.new("RGBA", (2 * r + 16, 2 * r + 16), (0, 0, 0, 0))
    g = ImageDraw.Draw(layer)
    ox = oy = r + 8
    g.ellipse([ox - r, oy - r, ox + r, oy + r], fill=(38, 84, 124, 255),
              outline=INK, width=4)
    for k in (-2, -1, 0, 1, 2):
        x = ox + k * r // 3
        xr = max(8, int(r * (1 - (k * 0.32) ** 2) ** 0.5))
        g.arc([x - xr, oy - r, x + xr, oy + r], 90, 270,
              fill=(140, 190, 210, 255), width=3)
    for k in (-1, 0, 1):
        y = oy + k * r // 2
        yr = int(r * (1 - (k * 0.42) ** 2) ** 0.5)
        g.arc([ox - yr, y - yr // 3, ox + yr, y + yr // 3], 0, 360,
              fill=(140, 190, 210, 255), width=3)
    # land blobs
    g.ellipse([ox - r * 0.55, oy - r * 0.62, ox - r * 0.05, oy - r * 0.18],
              fill=(96, 160, 90, 255))
    g.ellipse([ox + r * 0.08, oy + r * 0.05, ox + r * 0.58, oy + r * 0.55],
              fill=(96, 160, 90, 255))
    g.ellipse([ox - r * 0.75, oy + r * 0.28, ox - r * 0.35, oy + r * 0.62],
              fill=(120, 170, 100, 255))
    # red crack down the globe
    pts = [(ox - 6, oy - r + 6), (ox + 14, oy - r * 0.45),
           (ox - 10, oy - r * 0.05), (ox + 12, oy + r * 0.4),
           (ox - 4, oy + r - 8)]
    g.line(pts, fill=RED, width=7, joint="curve")
    # small flame above the crack
    fx, fy = ox + r * 0.55, oy - r * 0.75
    g.polygon([(fx, fy - 26), (fx + 14, fy + 2), (fx + 5, fy + 12),
               (fx - 5, fy + 12), (fx - 14, fy + 2)], fill=(230, 120, 30, 255))
    mask = Image.new("L", layer.size, 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([ox - r, oy - r, ox + r, oy + r], fill=255)
    return layer, mask, (cx - ox, cy - oy)


def draw_ship(draw, x, y, w, h):
    """Simple cargo ship with containers, flame and waves."""
    hull_y = y + h - 26
    draw.polygon([(x, hull_y), (x + w, hull_y), (x + w - 18, hull_y + 22),
                  (x + 14, hull_y + 22)], fill=(20, 33, 61))
    draw.rectangle([x + 16, hull_y - 34, x + 52, hull_y - 2], fill=RED)
    draw.rectangle([x + 56, hull_y - 34, x + 92, hull_y - 2], fill=GOLD)
    draw.rectangle([x + 96, hull_y - 22, x + 128, hull_y - 2], fill=TEAL)
    draw.rectangle([x + w - 52, hull_y - 52, x + w - 30, hull_y - 2],
                   fill=WHITE, outline=INK, width=2)
    # flame from the deck
    fx = x + w // 2
    draw.polygon([(fx, hull_y - 48), (fx + 14, hull_y - 26),
                  (fx + 5, hull_y - 16), (fx - 5, hull_y - 16),
                  (fx - 14, hull_y - 26)], fill=(230, 120, 30))
    draw.polygon([(fx, hull_y - 36), (fx + 7, hull_y - 20),
                  (fx - 7, hull_y - 20)], fill=(250, 200, 60))
    # waves
    for k in range(2):
        wy = hull_y + 28 + k * 8
        draw.arc([x - 6, wy - 8, x + w // 3, wy + 8], 0, 180,
                 fill=BLUE, width=3)
        draw.arc([x + w // 3, wy - 8, x + 2 * w // 3, wy + 8], 0, 180,
                 fill=BLUE, width=3)
        draw.arc([x + 2 * w // 3, wy - 8, x + w + 6, wy + 8], 0, 180,
                 fill=BLUE, width=3)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top red rule + masthead -------------------------------------
    d.rectangle([0, 0, W, 10], fill=RED)
    d.rectangle([0, 10, W, 102], fill=INK)
    d.text((28, 26), "THE WORLD IN ONE DAY", font=F_SERIF_B(44), fill=WHITE)
    d.text((28, 78), "MONDAY  •  23 NOVEMBER 2026", font=F_SANS_B(21),
           fill=(250, 200, 60))
    d.rectangle([W - 268, 24, W - 28, 88], outline=(250, 200, 60), width=3)
    d.text((W - 252, 32), "35 STORIES", font=F_SANS_B(24), fill=WHITE)
    d.text((W - 252, 60), "7 REGIONS", font=F_SANS_B(24), fill=WHITE)
    d.rectangle([0, 102, W, 108], fill=RED)

    # ---- hero: COP31 --------------------------------------------------
    d.text((28, 122), "CLIMATE  •  ANTALYA, TURKEY", font=F_SANS_B(19), fill=RED)
    d.text((28, 148), "COP31 COLLAPSES", font=F_SANS_B(64), fill=INK)
    deck = ("Nearly 200 nations leave Antalya with no climate deal. The EU "
            "walks out as the final text drops any mention of fossil fuels "
            "- the longest summit in history ends in failure.")
    y = 228
    for line in wrap(d, deck, F_SANS(23), 600):
        d.text((28, y), line, font=F_SANS(23), fill=(40, 52, 74))
        y += 30
    d.text((28, y + 8), "50+ HOURS OVERTIME  •  NO DEAL AFTER 2 WEEKS",
           font=F_SANS_B(18), fill=RED)
    globe, gmask, gpos = draw_globe(d, 862, 252, 112)
    img.paste(globe, gpos, gmask)
    d.rectangle([748, 356, 976, 388], fill=RED)
    d.text((760, 362), "NO DEAL IN ANTALYA", font=F_SANS_B(18), fill=WHITE)
    d.line([0, 400, W, 400], fill=INK, width=3)

    # ---- features row --------------------------------------------------
    # left: Democrats 258
    d.text((28, 416), "AMERICAS  •  WASHINGTON", font=F_SANS_B(16), fill=RED)
    d.text((28, 446), "258", font=F_SANS_B(64), fill=GOLD)
    d.text((180, 452), "DEMOCRATS TAKE", font=F_SANS_B(28), fill=INK)
    d.text((180, 486), "THE HOUSE", font=F_SANS_B(28), fill=INK)
    feat1 = ("Biggest majority since 1992. Hubbard's North Carolina win "
             "seals at least 258 seats.")
    y = 530
    for line in wrap(d, feat1, F_SANS(17), 460):
        d.text((28, y), line, font=F_SANS(17), fill=(40, 52, 74))
        y += 22
    d.line([512, 412, 512, 580], fill=SLATE, width=2)
    # right: Sparta II
    d.text((540, 416), "EUROPE  •  GULF OF FINLAND", font=F_SANS_B(16), fill=RED)
    draw_ship(d, 540, 442, 180, 70)
    d.text((736, 452), "SPARTA II STILL", font=F_SANS_B(24), fill=INK)
    d.text((736, 484), "BURNING", font=F_SANS_B(24), fill=INK)
    feat2 = ("Russian cargo ship ablaze in the Baltic after a drone strike; "
             "all 16 crew rescued as Finland tows her out.")
    y = 542
    for line in wrap(d, feat2, F_SANS(16), 456):
        d.text((540, y), line, font=F_SANS(17), fill=(40, 52, 74))
        y += 22
    d.line([0, 584, W, 584], fill=INK, width=3)

    # ---- numbers band ---------------------------------------------------
    numbers = [
        ("258", "HOUSE SEATS"),
        ("14", "TRAPPED IN KYIV"),
        ("36", "MISSING IN JAVA"),
        ("50+", "COP31 OVERTIME HRS"),
        ("~200", "NATIONS, NO DEAL"),
        ("24", "KILLED IN S. SUDAN"),
        ("720", "INDIA'S RECORD RUNS"),
    ]
    d.rectangle([0, 584, W, 652], fill=(20, 33, 61))
    seg = W // 7
    for i, (num, label) in enumerate(numbers):
        cx = i * seg + seg // 2
        wnum = d.textlength(num, font=F_SANS_B(28))
        d.text((cx - wnum / 2, 594), num, font=F_SANS_B(28),
               fill=(250, 200, 60))
        wlab = d.textlength(label, font=F_SANS_B(10))
        d.text((cx - wlab / 2, 628), label, font=F_SANS_B(10), fill=WHITE)
        if i:
            d.line([i * seg, 594, i * seg, 642], fill=(90, 100, 114), width=1)

    # ---- region strip ----------------------------------------------------
    regions = [("EUROPE", 9), ("MIDDLE EAST", 7), ("AMERICAS", 5),
               ("ASIA", 6), ("AFRICA", 3), ("OCEANIA", 2), ("WORLD", 3)]
    x = 28
    d.text((28, 660), "REGIONS:", font=F_SANS_B(15), fill=SLATE)
    x = 118
    for name, count in regions:
        chip = "%s %d" % (name, count)
        wch = d.textlength(chip, font=F_SANS_B(15)) + 18
        d.rounded_rectangle([x, 658, x + wch, 682], radius=11,
                            outline=INK, width=2)
        d.text((x + 9, 662), chip, font=F_SANS_B(15), fill=INK)
        x += wch + 10
    d.line([0, 690, W, 690], fill=INK, width=2)

    # ---- briefs grid ------------------------------------------------------
    # (region, headline) — every story happened or was first reported
    # on Monday 23 November 2026, verified against live news sources.
    briefs = [
        ("EUROPE", "Kyiv flats hit: 14 feared trapped after drone strike"),
        ("EUROPE", "UK to build Ukrainian drones in new defence deal"),
        ("EUROPE", "Thousands march in Lisbon over living costs"),
        ("EUROPE", "Poland: Russia twice tried to kill US-Ukrainian rapper"),
        ("EUROPE", "Ferrari: Hamilton-Leclerc crash 'unacceptable'"),
        ("EUROPE", "Liverpool rout 10-man Man Utd in Pochettino's debut"),
        ("EUROPE", "Jeweller Paolo Bulgari dies aged 89"),
        ("M. EAST", "Hormuz war at crucial stage as fighting hits Gulf"),
        ("M. EAST", "Saudi-led coalition intercepts Houthi missile"),
        ("M. EAST", "Tehran hits 3 tankers, shows off missile systems"),
        ("M. EAST", "Bahrain attacked again as Iran war widens"),
        ("M. EAST", "Tanker incident with military forces off Oman"),
        ("M. EAST", "Eisenkot: settler violence is 'Jewish terrorism'"),
        ("M. EAST", "Pakistan FM hopeful of US-Iran deal, warns on war"),
        ("AMERICAS", "US seeks answers on Nvidia chips sold to China"),
        ("AMERICAS", "'El Chapo Isidro' captured; 11 dead in Sinaloa"),
        ("AMERICAS", "Paredes collapses in post-match TV interview"),
        ("AMERICAS", "Brazil deputy details Lula's 'digital army'"),
        ("ASIA", "S. Korea minister quits over AI exam-cheating scandal"),
        ("ASIA", "Nepal PM Balendra Shah in Delhi for talks with Modi"),
        ("ASIA", "Java factory fire: 3 dead, 36 missing in Serang"),
        ("ASIA", "Myanmar junta calls ASEAN decision 'unfair'"),
        ("ASIA", "India A lose to Pakistan A in Rising Stars thriller"),
        ("ASIA", "BJP MP Ramrao Wadkute dies in Delhi"),
        ("AFRICA", "WHO: fighting near Congo Ebola outbreak disrupts aid"),
        ("AFRICA", "SPLA-IO attack kills 24 civilians in South Sudan"),
        ("AFRICA", "Russian warship Mercury mostly sunk off Benghazi"),
        ("OCEANIA", "India post record 720/9d in Wellington Test"),
        ("OCEANIA", "Wales coach rues defeat by Australia"),
        ("WORLD", "UN: talks on lethal AI weapons to continue"),
        ("WORLD", "World chess championship: the geniuses at work"),
        ("WORLD", "Gastric Cancer Awareness Month: the global picture"),
    ]
    assert len(briefs) == 32, len(briefs)
    assert sum(c for _, c in regions) == 35
    col_w = 486
    row_h = 19
    y0 = 700
    for i, (tag, head) in enumerate(briefs):
        col = i % 2
        row = i // 2
        bx = 28 + col * 500
        by = y0 + row * row_h
        d.text((bx, by), tag, font=F_SANS_B(12), fill=RED)
        tag_w = d.textlength(tag, font=F_SANS_B(12))
        line = fit_one_line(d, head, F_SANS(13), col_w - tag_w - 12)
        d.text((bx + tag_w + 8, by), line, font=F_SANS(13), fill=INK)

    # ---- footer ------------------------------------------------------------
    d.rectangle([0, 1002, W, H], fill=INK)
    d.text((28, 1008), "DATE CHECK — MONDAY 23 NOVEMBER 2026",
           font=F_SANS_B(14), fill=(250, 200, 60))
    d.text((560, 1008), "Sources: Reuters, AP, BBC, The Hindu",
           font=F_SANS(13), fill=WHITE)

    img.save(OUT, "PNG", optimize=True)
    os.chmod(OUT, 0o644)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
