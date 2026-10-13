"""Hand-drawn, black & white slide decks.

Describe slides in Python with this module, then `Deck.save(out_dir)` writes:

- ``spec.json``  — consumed by ``scripts/build_pptx.js`` (native, editable PPTX shapes and text)
- ``deck.html``  — rendered by ``scripts/render.js`` (Chromium) for PNG previews and the PDF

Both outputs come from the same layout, so what you check in the preview is what lands in the PPTX.
All coordinates are inches. The default canvas is 16:9 widescreen (13.333 x 7.5).
"""
import html
import json
import math
import os
import random

from fontTools.ttLib import TTFont

W_DEFAULT, H_DEFAULT = 13.333, 7.5
PX = 96  # CSS px per inch

# Characters that must not start a line (Chinese line-breaking rules).
NO_LINE_START = set('，。、；：？！）」』》%,.;:!?)')


# --------------------------------------------------------------------------- font metrics
class Metrics:
    """Real advance widths from the font file, so wrapping matches the renderers."""

    def __init__(self, font_path):
        f = TTFont(font_path)
        self.cmap = f.getBestCmap()
        self.hmtx = f['hmtx']
        self.upm = f['head'].unitsPerEm
        self.missing = set()

    def width(self, s, pt):
        total = 0
        for ch in s:
            g = self.cmap.get(ord(ch))
            if g is None:
                self.missing.add(ch)
                total += self.upm
            else:
                total += self.hmtx[g][0]
        return total / self.upm * pt / 72

    def wrap(self, text, width, pt):
        """Greedy wrap: keeps ASCII words/numbers together and never starts a line with closing punctuation."""
        lines = []
        for para in text.split('\n'):
            tokens, buf = [], ''
            for ch in para:
                if ord(ch) < 128 and ch != ' ':
                    buf += ch
                else:
                    if buf:
                        tokens.append(buf)
                        buf = ''
                    tokens.append(ch)
            if buf:
                tokens.append(buf)
            line = ''
            for tk in tokens:
                if line and self.width(line + tk, pt) > width:
                    if tk in NO_LINE_START and len(line) > 1:
                        lines.append(line[:-1].rstrip())
                        line = line[-1] + tk
                    else:
                        lines.append(line.rstrip())
                        line = tk.lstrip()
                else:
                    line += tk
            lines.append(line.rstrip())
        return lines


# --------------------------------------------------------------------------- rough pen
class Pen:
    """Generates wobbly polylines in the style of rough.js (double strokes, overshooting corners)."""

    def __init__(self, seed, roughness=1.0):
        self.r = random.Random(seed)
        self.k = roughness

    def _line(self, p1, p2, amp):
        amp *= self.k
        (x1, y1), (x2, y2) = p1, p2
        length = math.hypot(x2 - x1, y2 - y1) or 1e-6
        nx, ny = -(y2 - y1) / length, (x2 - x1) / length
        n = max(6, int(length * 10))
        a = amp * min(1.0, 0.35 + length / 3)
        ph1, ph2 = self.r.uniform(0, 6.28), self.r.uniform(0, 6.28)
        f1, f2 = self.r.uniform(0.6, 1.4), self.r.uniform(1.8, 3.0)
        bow = self.r.uniform(-1, 1) * a * 0.8
        j = lambda: self.r.uniform(-0.015, 0.015) * self.k
        sx, sy, ex, ey = x1 + j(), y1 + j(), x2 + j(), y2 + j()
        pts = []
        for i in range(n + 1):
            t = i / n
            off = (a * 0.5 * math.sin(ph1 + f1 * t * 6.28) + a * 0.25 * math.sin(ph2 + f2 * t * 6.28)
                   + bow * math.sin(t * math.pi)) * math.sin(t * math.pi) ** 0.5
            pts.append((sx + (ex - sx) * t + nx * off, sy + (ey - sy) * t + ny * off))
        return pts

    def line(self, p1, p2, amp=0.05, double=True):
        paths = [self._line(p1, p2, amp)]
        if double:
            paths.append(self._line(p1, p2, amp * 0.8))
        return paths

    def rect(self, x, y, w, h, amp=0.045, double=True):
        o = lambda: self.r.uniform(0.03, 0.1) * self.k  # corner overshoot
        out = []
        for _ in range(2 if double else 1):
            out.append(self._line((x - o(), y), (x + w + o(), y), amp))
            out.append(self._line((x + w, y - o()), (x + w, y + h + o()), amp))
            out.append(self._line((x + w + o(), y + h), (x - o(), y + h), amp))
            out.append(self._line((x, y + h + o()), (x, y - o()), amp))
        return out

    def ellipse(self, cx, cy, rx, ry, double=True):
        out = []
        for _ in range(2 if double else 1):
            start = self.r.uniform(0, 6.28)
            sweep = 6.28 + self.r.uniform(0.15, 0.45)  # loop does not close exactly
            ph = self.r.uniform(0, 6.28)
            pts = []
            for i in range(65):
                t = start + sweep * i / 64
                k = 1 + (0.05 * math.sin(ph + 2 * t) + 0.015 * math.sin(ph * 2 + 5 * t)) * self.k
                pts.append((cx + rx * k * math.cos(t), cy + ry * k * math.sin(t)))
            out.append(pts)
        return out

    def arrow(self, p1, p2, head=0.16):
        out = self.line(p1, p2, amp=0.03)
        (x1, y1), (x2, y2) = p1, p2
        ang = math.atan2(y2 - y1, x2 - x1)
        for s in (1, -1):
            a2 = ang + math.pi - s * math.radians(28)
            out += self.line((x2, y2), (x2 + head * math.cos(a2), y2 + head * math.sin(a2)), amp=0.01, double=False)
        return out

    def check(self, x, y, s=0.24):
        return [self._line((x, y + s * 0.55), (x + s * 0.38, y + s), 0.01)
                + self._line((x + s * 0.38, y + s), (x + s, y), 0.015)[1:]]

    def cross(self, x, y, s=0.22):
        return self.line((x, y), (x + s, y + s), 0.01, False) + self.line((x + s, y), (x, y + s), 0.01, False)

    def blob(self, x, y, w, h):
        """Closed, irregular marker-like shape (for black fills)."""
        pts = []
        cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2
        ph = self.r.uniform(0, 6.28)
        for i in range(48):
            t = 6.28 * i / 48
            c, s = math.cos(t), math.sin(t)
            px = cx + rx * (abs(c) ** 0.18) * (1 if c >= 0 else -1)
            py = cy + ry * (abs(s) ** 0.35) * (1 if s >= 0 else -1)
            k = (0.035 * math.sin(ph + 3 * t) + 0.02 * math.sin(ph * 1.7 + 7 * t)) * self.k
            pts.append((px + k, py + k * 0.8 + (px - cx) * 0.012))
        return pts


# --------------------------------------------------------------------------- slides
class Slide:
    def __init__(self, deck, title=None, notes=''):
        self.deck = deck
        self.items = []
        self.notes = notes
        self.pen = Pen(deck.seed + len(deck.slides) * 7919 + 13, deck.roughness)
        if title:
            t = deck.style
            self.text(t['margin_x'], t['title_y'], deck.W - 2 * t['margin_x'], title, t['title_pt'])

    # ---- primitives
    def stroke(self, paths, width=1.75):
        self.items.append({'type': 'stroke', 'paths': paths, 'width': width})

    def fill(self, pts):
        self.items.append({'type': 'fill', 'pts': pts})

    def text(self, x, y, w, s, pt, align='left', color='000000', wrap=True):
        """Top-anchored text. Returns the height used (inches)."""
        m = self.deck.metrics
        lines = m.wrap(s, w, pt) if wrap else s.split('\n')
        for ln in lines:
            lw = m.width(ln, pt)
            if lw > w + 0.01:
                self.deck.warn(f'slide {self.index}: text overflows box ({lw:.2f}" > {w:.2f}"): {ln!r}')
        h = len(lines) * pt * self.deck.LH / 72
        self.items.append({'type': 'text', 'x': x, 'y': y, 'w': w, 'h': h, 'lines': lines,
                           'pt': pt, 'align': align, 'color': color})
        return h

    def text_vc(self, x, y, w, h, s, pt, align='left', color='000000'):
        """Text vertically centred inside the band (y, h)."""
        lines = self.deck.metrics.wrap(s, w, pt)
        th = len(lines) * pt * self.deck.LH / 72
        return self.text(x, y + (h - th) / 2, w, '\n'.join(lines), pt, align, color, wrap=False)

    @property
    def index(self):
        return self.deck.slides.index(self) + 1 if self in self.deck.slides else len(self.deck.slides) + 1

    # ---- drawn shapes
    def box(self, x, y, w, h, double=True, width=1.75):
        self.stroke(self.pen.rect(x, y, w, h, double=double), width)

    def line(self, p1, p2, width=1.5, double=False):
        self.stroke(self.pen.line(p1, p2, amp=0.02, double=double), width)

    def arrow(self, p1, p2, head=0.14, width=1.75):
        self.stroke(self.pen.arrow(p1, p2, head), width)

    def ellipse(self, cx, cy, rx, ry, double=True, width=2):
        self.stroke(self.pen.ellipse(cx, cy, rx, ry, double), width)

    def frame(self, inset=0.45):
        """Sketchbook border around the whole slide (cover / closing slides)."""
        self.box(inset, inset - 0.05, self.deck.W - 2 * inset, self.deck.H - 2 * inset + 0.1, width=1.5)

    # ---- components
    def card(self, x, y, w, h, title, body=None, title_pt=20, body_pt=15, foot=None, foot_pt=13):
        """Box with a heading, optional body and optional footer line."""
        self.box(x, y, w, h)
        pad = 0.25
        cy = y + 0.18
        cy += self.text(x + pad, cy, w - 2 * pad, title, title_pt) + 0.18
        if body:
            self.text(x + pad, cy, w - 2 * pad, body, body_pt)
        if foot:
            self.text(x + pad, y + h - 0.2 - foot_pt * self.deck.LH / 72, w - 2 * pad, foot, foot_pt)

    def label(self, x, y, w, h, s, pt=18):
        """Black marker blob with white text: the one strong emphasis per slide."""
        self.fill(self.pen.blob(x, y, w, h))
        self.text_vc(x + 0.2, y, w - 0.4, h, s, pt, 'center', 'FFFFFF')

    def numbered(self, x, y, n, pt=18, r=0.3):
        self.ellipse(x + r, y + r, r, r, double=False, width=1.75)
        self.text(x, y + r - pt * self.deck.LH / 144, 2 * r, str(n), pt, 'center')

    def checklist(self, x, y, w, items, pt=15, gap=0.18, boxed=True):
        """Hand-drawn ticked items. Returns the y after the list."""
        for it in items:
            if boxed:
                self.stroke(self.pen.rect(x, y + 0.04, 0.22, 0.22, amp=0.01, double=False), 1.25)
            self.stroke(self.pen.check(x + 0.03, y - 0.04, 0.24), 1.75)
            y += self.text(x + 0.42, y, w - 0.42, it, pt) + gap
        return y

    def bullets(self, x, y, w, items, pt=15, gap=0.15):
        """Short hand-drawn dash before each item. Returns the y after the list."""
        for it in items:
            mid = y + pt * self.deck.LH / 144
            self.stroke(self.pen.line((x, mid), (x + 0.25, mid), amp=0.005, double=False), 2)
            y += self.text(x + 0.45, y, w - 0.45, it, pt) + gap
        return y

    def table(self, x, y, widths, row_h, rows, pt=15, head_pt=None):
        """Hand-drawn grid; rows[0] is the header. Returns the y below the table."""
        head_pt = head_pt or pt
        tw, n = sum(widths), len(rows)
        th = row_h * n
        self.box(x, y, tw, th, width=1.5)
        paths = []
        for i in range(1, n):
            paths += self.pen.line((x, y + i * row_h), (x + tw, y + i * row_h), amp=0.02, double=(i == 1))
        cx = x
        for wc in widths[:-1]:
            cx += wc
            paths += self.pen.line((cx, y), (cx, y + th), amp=0.02, double=False)
        self.stroke(paths, 1.25)
        for r, cells in enumerate(rows):
            cx = x
            for cell, wc in zip(cells, widths):
                self.text_vc(cx + 0.15, y + r * row_h, wc - 0.3, row_h, cell, head_pt if r == 0 else pt)
                cx += wc
        return y + th

    def flow(self, x, y, labels, box_w=1.75, box_h=0.75, gap=0.75, pt=18):
        """Row of boxes joined by arrows."""
        for i, lab in enumerate(labels):
            bx = x + i * (box_w + gap)
            self.box(bx, y, box_w, box_h, double=False)
            self.text_vc(bx, y, box_w, box_h, lab, pt, 'center')
            if i < len(labels) - 1:
                self.arrow((bx + box_w + 0.1, y + box_h / 2), (bx + box_w + gap - 0.1, y + box_h / 2))


class Deck:
    def __init__(self, font_path, font_name, width=W_DEFAULT, height=H_DEFAULT, line_height=1.25,
                 seed=1, roughness=1.0, page_numbers=True, title='Deck'):
        self.font_path = os.path.abspath(font_path)
        self.font_name = font_name
        self.W, self.H, self.LH = width, height, line_height
        self.seed, self.roughness = seed, roughness
        self.page_numbers = page_numbers
        self.title = title
        self.metrics = Metrics(font_path)
        self.slides = []
        self.warnings = []
        self.style = {'margin_x': 0.75, 'title_y': 0.42, 'title_pt': 32, 'content_y': 1.6}

    def slide(self, title=None, notes=''):
        s = Slide(self, title, notes)
        self.slides.append(s)
        return s

    def warn(self, msg):
        self.warnings.append(msg)

    def columns(self, n, x=0.8, width=None, gap=0.32):
        """Equal columns across the content width: list of (x, w)."""
        width = width if width is not None else self.W - 2 * x
        w = (width - gap * (n - 1)) / n
        return [(x + i * (w + gap), w) for i in range(n)]

    # ------------------------------------------------------------------ output
    def save(self, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        if self.page_numbers and not getattr(self, '_numbered', False):
            self._numbered = True
            for s in self.slides[1:]:
                s.text(self.W - 1.33, self.H - 0.55, 0.75, f'{s.index:02d}', 12, 'right')
        if self.metrics.missing:
            self.warn('font has no glyph for: ' + ''.join(sorted(self.metrics.missing))
                      + ' — reword, or draw it (arrows, checks) instead of typing it')
        spec = {'font': self.font_name, 'title': self.title, 'W': self.W, 'H': self.H, 'LH': self.LH,
                'slides': [{'items': s.items, 'notes': s.notes} for s in self.slides]}
        with open(os.path.join(out_dir, 'spec.json'), 'w', encoding='utf-8') as f:
            json.dump(spec, f, ensure_ascii=False)
        with open(os.path.join(out_dir, 'deck.html'), 'w', encoding='utf-8') as f:
            f.write(self._html())
        for w in self.warnings:
            print('WARNING:', w)
        print(f'{len(self.slides)} slides -> {out_dir}/spec.json, {out_dir}/deck.html')
        return len(self.warnings)

    def _html(self):
        def d(paths):
            return ' '.join('M' + ' L'.join(f'{x * PX:.1f},{y * PX:.1f}' for x, y in p) for p in paths)

        secs = []
        for s in self.slides:
            svg, txt = [], []
            for it in s.items:
                if it['type'] == 'stroke':
                    svg.append(f'<path d="{d(it["paths"])}" fill="none" stroke="#000" stroke-width="{it["width"] * PX / 72:.2f}" '
                               'stroke-linecap="round" stroke-linejoin="round"/>')
                elif it['type'] == 'fill':
                    svg.append(f'<path d="{d([it["pts"]])} Z" fill="#000"/>')
                else:
                    body = '<br>'.join(html.escape(l) for l in it['lines'])
                    txt.append(f'<div class="t" style="left:{it["x"] * PX:.1f}px;top:{it["y"] * PX:.1f}px;width:{it["w"] * PX:.1f}px;'
                               f'font-size:{it["pt"]}pt;text-align:{it["align"]};color:#{it["color"]}">{body}</div>')
            secs.append(f'<section><svg width="{self.W * PX:.0f}" height="{self.H * PX:.0f}">{"".join(svg)}</svg>{"".join(txt)}</section>')
        return (f'<!doctype html><html><head><meta charset="utf-8"><style>'
                f'@font-face{{font-family:"{self.font_name}";src:url("file://{self.font_path}");}}'
                f'@page{{size:{self.W}in {self.H}in;margin:0}}'
                'html,body{margin:0;padding:0;background:#fff}'
                f'section{{position:relative;width:{self.W * PX:.0f}px;height:{self.H * PX:.0f}px;overflow:hidden;background:#fff;page-break-after:always}}'
                'svg{position:absolute;left:0;top:0}'
                f'.t{{position:absolute;font-family:"{self.font_name}";line-height:{self.LH};white-space:nowrap}}'
                f'</style></head><body>{"".join(secs)}</body></html>')
