#!/usr/bin/env python3
"""Put numbered callouts on a screenshot.

A screenshot of a dense interface tells a reader almost nothing on its own:
they have to find the control the prose is talking about, and in a panel with
forty buttons that is most of the work. A numbered box around the right
control removes it.

The numbers are drawn on the image rather than listed beside it so the pairing
survives being copied into a slide, printed, or read on a phone where the
caption has wrapped somewhere else.

Usage, as a library:

    from annotate import annotate
    annotate("in.jpg", "out.webp", [
        (x, y, w, h, "1"),
        (x, y, w, h, "2"),
    ], caption="Starting the array")

Coordinates are in the source image's own pixels.
"""
import pathlib

from PIL import Image, ImageDraw, ImageFont

ACCENT = (0, 255, 230)        # the same cyan the site uses for diagrams
SHADOW = (10, 12, 16)
CAPTION_BG = (18, 20, 25)

_FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _font(size):
    for f in _FONTS:
        if pathlib.Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
    return ImageFont.load_default()


def annotate(src, dst, marks, caption=None, scale=2):
    """Draw numbered boxes on `src` and write `dst`.

    `marks` is a list of (x, y, w, h, label). `scale` upsamples first so the
    strokes and numerals stay crisp on a high-density screen; a screenshot
    taken at 800px wide is otherwise unreadable once a browser scales it.
    """
    im = Image.open(src).convert("RGB")
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    d = ImageDraw.Draw(im, "RGBA")

    r = 15 * scale                      # callout circle radius
    box_w = max(2, round(1.5 * scale))
    f_num = _font(int(19 * scale))

    for (x, y, w, h, label) in marks:
        x, y, w, h = x * scale, y * scale, w * scale, h * scale
        # Dim nothing: a screenshot is evidence, so the original pixels stay
        # readable and the annotation sits on top of them.
        d.rounded_rectangle([x, y, x + w, y + h], radius=6 * scale,
                            outline=ACCENT, width=box_w)
        # The badge hangs off the top-left corner, clamped into frame so a
        # control at the very edge still gets a visible number.
        cx = max(r + 2, x - r // 2)
        cy = max(r + 2, y - r // 2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SHADOW, outline=ACCENT,
                  width=box_w)
        tb = d.textbbox((0, 0), label, font=f_num)
        d.text((cx - (tb[2] - tb[0]) / 2, cy - (tb[3] - tb[1]) / 2 - tb[1]),
               label, font=f_num, fill=ACCENT)

    if caption:
        f_cap = _font(int(15 * scale))
        pad = 10 * scale
        # Wrap to the image width. An unwrapped caption is silently cropped at
        # the right edge, which loses the last steps precisely when the list
        # is long enough to need numbering.
        words, lines, cur = caption.split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if d.textlength(trial, font=f_cap) > im.width - pad * 2 and cur:
                lines.append(cur)
                cur = w
            else:
                cur = trial
        if cur:
            lines.append(cur)
        lh = int(f_cap.size * 1.45)
        bar = lh * len(lines) + pad * 2
        out = Image.new("RGB", (im.width, im.height + bar), CAPTION_BG)
        out.paste(im, (0, 0))
        d2 = ImageDraw.Draw(out)
        for i, line in enumerate(lines):
            d2.text((pad, im.height + pad + i * lh), line, font=f_cap,
                    fill=(222, 226, 233))
        im = out

    dst = pathlib.Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, quality=88, method=6)
    return im.size


def demo():
    """Self-check: the output exists, is bigger than the input, and the
    accent colour actually landed on the pixels."""
    import tempfile
    src = pathlib.Path(tempfile.mkdtemp()) / "in.png"
    Image.new("RGB", (200, 120), (30, 30, 30)).save(src)
    dst = src.parent / "out.webp"
    size = annotate(src, dst, [(20, 20, 60, 30, "1")], caption="x", scale=2)
    assert dst.exists(), "no output written"
    assert size[0] == 400, size
    px = Image.open(dst).convert("RGB").getdata()
    assert any(abs(p[1] - 255) < 40 and abs(p[2] - 230) < 50 and p[0] < 90
               for p in px), "accent colour not drawn"
    print("self-check ok")


if __name__ == "__main__":
    demo()
