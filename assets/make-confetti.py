"""Confetti banner for the Google Chat card, animated and static.

The animation plays once and settles rather than looping forever. A banner
that never stops moving is fine the first time and irritating by the fortieth,
and this one appears on every thank-you the team sends.

Confetti falls under gravity, tumbles as it goes, and the wordmark fades up
underneath it.
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 280
S = 2                      # supersample; GIF palettes punish more than this
FRAMES = 26
HOLD_MS = 2600             # pause on the final frame before the loop ends

PAPER   = (244, 242, 236)
INK     = (27, 26, 22)
CONFETTI = [
    (200, 106, 12),        # accent
    (232, 145, 44),        # accent bright
    (107, 58, 94),         # plum
    (197, 143, 184),       # plum light
    (61, 122, 78),         # good
    (240, 200, 120),       # straw
]

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bricolage.ttf")


def make_pieces(n=78, seed=5):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        out.append(dict(
            x0=r.uniform(-0.05, 1.05),           # fraction of width
            y0=r.uniform(-1.15, -0.05),          # starts above the frame
            vx=r.uniform(-0.05, 0.05),
            spin=r.uniform(-3.0, 3.0),
            a0=r.uniform(0, 360),
            w=r.uniform(11, 22),
            h=r.uniform(6, 11),
            col=r.choice(CONFETTI),
            round=r.random() < 0.26,
            land=r.uniform(0.30, 1.02),          # where it comes to rest
            ease=r.uniform(0.85, 1.15),
        ))
    return out


def draw_piece(base, p, t):
    """t runs 0..1. Vertical travel eases out so pieces settle rather than stop dead."""
    e = 1 - pow(1 - min(t * p["ease"], 1.0), 2.2)
    y = (p["y0"] + (p["land"] - p["y0"]) * e) * H * S
    x = (p["x0"] + p["vx"] * e) * W * S
    if y < -60 or y > H * S + 60:
        return
    ang = p["a0"] + p["spin"] * 360 * e
    w, h = p["w"] * S, p["h"] * S

    tile = Image.new("RGBA", (int(w * 2), int(h * 2)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    box = [w * 0.5, h * 0.5, w * 1.5, h * 1.5]
    if p["round"]:
        td.ellipse(box, fill=p["col"] + (255,))
    else:
        td.rounded_rectangle(box, radius=max(1, int(h * 0.22)), fill=p["col"] + (255,))
    tile = tile.rotate(ang, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(tile, (int(x - tile.width / 2), int(y - tile.height / 2)))


def wordmark(base, alpha):
    if alpha <= 0:
        return
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = ImageFont.truetype(FONT, int(84 * S))
    text = "Thank you"
    bb = d.textbbox((0, 0), text, font=f)
    x = (W * S - (bb[2] - bb[0])) / 2 - bb[0]
    y = (H * S - (bb[3] - bb[1])) / 2 - bb[1]
    d.text((x, y), text, font=f, fill=INK + (int(255 * alpha),))
    base.alpha_composite(layer)


def frame(pieces, t, word_alpha):
    im = Image.new("RGBA", (W * S, H * S), PAPER + (255,))
    wordmark(im, word_alpha)                 # sits behind the confetti
    for p in pieces:
        draw_piece(im, p, t)
    return im.convert("RGB").resize((W, H), Image.LANCZOS)


def build(outdir):
    pieces = make_pieces()
    frames = []
    for i in range(FRAMES):
        t = i / (FRAMES - 1)
        # the words fade up over the first half, then hold
        wa = min(1.0, max(0.0, (t - 0.10) / 0.38))
        frames.append(frame(pieces, t, wa))

    still = frames[-1]
    still.save(os.path.join(outdir, "chat-confetti.png"), "PNG", optimize=True)

    durations = [70] * (FRAMES - 1) + [HOLD_MS]
    frames[0].save(
        os.path.join(outdir, "chat-confetti.gif"),
        save_all=True, append_images=frames[1:],
        duration=durations, loop=1, optimize=True, disposal=2)

    for f in ("chat-confetti.png", "chat-confetti.gif"):
        p = os.path.join(outdir, f)
        print("%-22s %7.1f KB" % (f, os.path.getsize(p) / 1024))


if __name__ == "__main__":
    build(sys.argv[1])
