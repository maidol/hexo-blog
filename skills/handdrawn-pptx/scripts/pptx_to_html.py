#!/usr/bin/env python3
"""Independent check of a built PPTX: redraw every slide from the PPTX XML itself
(custom-geometry paths + text boxes) as HTML, so it can be rendered and diffed against
the design render. Catches geometry/scaling/text mistakes without PowerPoint or LibreOffice.

usage: pptx_to_html.py deck.pptx check.html font.ttf
"""
import html
import os
import sys
import zipfile

from lxml import etree

pptx, out, font = sys.argv[1:4]
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
EMU, PX = 914400, 96

z = zipfile.ZipFile(pptx)
pres = etree.fromstring(z.read('ppt/presentation.xml'))
size = pres.find('p:sldSz', NS)
W, H = int(size.get('cx')) / EMU * PX, int(size.get('cy')) / EMU * PX
rels = {r.get('Id'): r.get('Target') for r in etree.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
order = [rels[s.get(RID)] for s in pres.find('p:sldIdLst', NS)]


def px(v):
    return v / EMU * PX


sections = []
for target in order:
    root = etree.fromstring(z.read('ppt/' + target))
    svg, txt = [], []
    for sp in root.iter('{%s}sp' % NS['p']):
        off, ext = sp.find('.//a:xfrm/a:off', NS), sp.find('.//a:xfrm/a:ext', NS)
        x, y, cx, cy = int(off.get('x')), int(off.get('y')), int(ext.get('cx')), int(ext.get('cy'))
        geo = sp.find('.//a:custGeom', NS)
        if geo is not None:
            path = geo.find('.//a:path', NS)
            pw, ph = int(path.get('w')), int(path.get('h'))
            d = []
            for el in path:
                tag = etree.QName(el).localname
                if tag in ('moveTo', 'lnTo'):
                    pt = el.find('a:pt', NS)
                    d.append(('M' if tag == 'moveTo' else 'L')
                             + f'{px(x + int(pt.get("x")) * cx / pw):.1f},{px(y + int(pt.get("y")) * cy / ph):.1f}')
                elif tag == 'close':
                    d.append('Z')
            sppr = sp.find('p:spPr', NS)
            if sppr.find('a:solidFill', NS) is not None:
                svg.append(f'<path d="{" ".join(d)}" fill="#000"/>')
            else:
                ln = sppr.find('a:ln', NS)
                w = int(ln.get('w', '0')) / 12700 if ln is not None else 0
                svg.append(f'<path d="{" ".join(d)}" fill="none" stroke="#000" stroke-width="{w * PX / 72:.2f}" '
                           'stroke-linecap="round" stroke-linejoin="round"/>')
        body = sp.find('p:txBody', NS)
        if body is None:
            continue
        rpr = body.find('.//a:rPr', NS)
        if rpr is None:
            continue
        paras = [''.join(t.text or '' for t in p.iter('{%s}t' % NS['a'])) for p in body.findall('a:p', NS)]
        size_pt = int(rpr.get('sz')) / 100
        color = rpr.find('.//a:srgbClr', NS).get('val')
        align = {'l': 'left', 'ctr': 'center', 'r': 'right'}[body.find('.//a:pPr', NS).get('algn', 'l')]
        spc = body.find('.//a:spcPts', NS)
        lh = f'{int(spc.get("val")) / 100}pt' if spc is not None else '1.2'
        txt.append(f'<div style="position:absolute;left:{px(x):.1f}px;top:{px(y):.1f}px;width:{px(cx):.1f}px;'
                   f'font:{size_pt}pt/{lh} \'F\';text-align:{align};color:#{color};white-space:pre-wrap">'
                   + '<br>'.join(html.escape(p) for p in paras) + '</div>')
    sections.append(f'<section><svg width="{W:.0f}" height="{H:.0f}" style="position:absolute">{"".join(svg)}</svg>'
                    f'{"".join(txt)}</section>')

with open(out, 'w', encoding='utf-8') as f:
    f.write(f'<!doctype html><meta charset="utf-8"><style>@font-face{{font-family:F;src:url("file://{os.path.abspath(font)}")}}'
            f'body{{margin:0}}section{{position:relative;width:{W:.0f}px;height:{H:.0f}px;overflow:hidden;background:#fff}}'
            '</style>' + ''.join(sections))
print(f'{len(sections)} slides -> {out}')
