#!/usr/bin/env python3
"""Deterministic front-page PNG for make.fun news-image-20261120.
News items from ~/workspace/goals/goal/hidden_files/news-image-20261120-prep.md
(verified via news search 2026-11-20 18:28 CST). No network, no timestamps
in the image, fixed fonts -> identical bytes every run. Layout flows by
measured y so nothing overlaps or clips; assert keeps it inside 1024px.
Verified 2026-11-21: entry.png sha256 =
3f46b62dbf1bd2f5be0f519ac844e8f43e8b6d6511da748e5ac9d0e873aa48db (124319 bytes).
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (178, 34, 34)
GREY = (90, 86, 78)
RULE = (17, 17, 17)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
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

def para(draw, x, y, text, fnt, max_w, leading, color=INK):
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
M = 36
CW = W - 2 * M

# top dateline bar
d.text((M, 20), "FRIDAY 20 NOVEMBER 2026", font=font(SANS_B, 21), fill=INK)
r = "ONE IMAGE  •  THE WORLD'S NEWS"
d.text((W - M - d.textlength(r, font=font(SANS_B, 21)), 20), r, font=font(SANS_B, 21), fill=GREY)
d.line([(M, 52), (W - M, 52)], fill=RULE, width=3)

# masthead
mast = "THE WORLD"
mf = font(SERIF_B, 104)
d.text(((W - d.textlength(mast, font=mf)) // 2, 58), mast, font=mf, fill=INK)
sub = "—  SUMMED UP IN ONE IMAGE  —"
sf = font(SANS_B, 23)
d.text(((W - d.textlength(sub, font=sf)) // 2, 176), sub, font=sf, fill=RED)
d.line([(M, 212), (W - M, 212)], fill=RULE, width=4)
d.line([(M, 219), (W - M, 219)], fill=RULE, width=2)

# LEAD: Anthropic IPO (headline width 620, chart on the right)
y = 232
d.text((M, y), "LEAD  •  MARKETS", font=font(SANS_B, 21), fill=RED)
y += 32
y = para(d, M, y, "ANTHROPIC IPO: First pure AI firm to go public", font(SERIF_B, 47), 620, 54)
y += 6
y = para(d, M, y, "Debut makes it one of the world's most valuable listed firms — even as AI stocks sell off.",
         font(SERIF, 22), 600, 29, color=(40, 40, 40))
lead_bottom = y
# chart box, right of lead
bx, by, bw, bh = 700, 232, 288, 168
d.rectangle([bx, by, bx + bw, by + bh], outline=INK, width=3)
d.text((bx + 14, by + 10), "AI STOCKS: UP, THEN DOWN", font=font(SANS_B, 16), fill=GREY)
pts = [(bx+20, by+140), (bx+70, by+115), (bx+120, by+88), (bx+170, by+55), (bx+220, by+78), (bx+268, by+105)]
d.line(pts, fill=RED, width=5, joint="curve")
for (px, py) in pts:
    d.ellipse([px-5, py-5, px+5, py+5], fill=RED)
d.text((bx + 14, by + bh - 26), "Debut day: a record listing", font=font(SANS, 16), fill=GREY)

y = max(lead_bottom, by + bh) + 14
d.line([(M, y), (W - M, y)], fill=RULE, width=2)
y += 14

# two-column stories
col_w = (CW - 24) // 2
def story(x, yy, tag, head, body):
    d.text((x, yy), tag, font=font(SANS_B, 19), fill=RED)
    yy += 28
    yy = para(d, x, yy, head, font(SERIF_B, 30), col_w, 34)
    yy += 4
    yy = para(d, x, yy, body, font(SERIF, 20), col_w, 24, color=(40, 40, 40))
    return yy

y1 = story(M, y, "WORLD COURT", "MYANMAR GUILTY OF GENOCIDE",
           "The Court finds Myanmar committed genocide against the Rohingya, 9–6, in northern Rakhine.")
y2 = story(M + col_w + 24, y, "CLIMATE  •  COP31", "FOSSIL FUELS CUT FROM DEAL",
           "Near-final texts drop the fossil-fuel transition as COP31 wraps.")
y = max(y1, y2) + 12
d.line([(M, y), (W - M, y)], fill=RULE, width=2)
y += 14
y1 = story(M, y, "WAR IN EUROPE", "RUSSIA HITS THREE KYIV BRIDGES",
           "A major missile attack strikes three bridges. The UK pledges 1,000+ drones in a £260m package.")
y2 = story(M + col_w + 24, y, "DIPLOMACY  •  APEC", "TRUMP–XI–PUTIN MEET",
           "A historic trilateral meeting and a 'peace declaration' on the APEC sidelines in China.")
y = max(y1, y2) + 12
d.line([(M, y), (W - M, y)], fill=RULE, width=3)
y += 12

# bottom strip
d.text((M, y), "ALSO TODAY", font=font(SANS_B, 19), fill=RED)
y += 28
y = para(d, M, y, "US SENATE VOTES UNANIMOUSLY TO RELEASE THE EPSTEIN FILES.",
         font(SERIF_B, 23), CW, 27)
y += 2
y = para(d, M, y, "Van Gogh sells for a record $190.4m  •  Potatoes grown in moon soil.",
         font(SERIF, 21), CW, 27, color=(40, 40, 40))
assert y <= 1000, f"layout overflow: y={y}"
d.line([(M, 1002), (W - M, 1002)], fill=RULE, width=2)

img.save("entry.png", format="PNG", optimize=True)
print(f"saved entry.png, bottom y={y}")
