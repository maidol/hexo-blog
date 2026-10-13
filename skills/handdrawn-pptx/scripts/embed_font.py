#!/usr/bin/env python3
"""Embed a TrueType font into a PPTX (so the handwriting shows without installing it) and
remove outlines from the black label shapes.

usage: embed_font.py raw.pptx deck.pptx font.ttf "Font Family Name"

The full font is embedded (not a subset), so edited text keeps rendering. The font's
OS/2 fsType must allow embedding (0 = installable, e.g. OFL fonts).
"""
import re
import sys
import zipfile

from fontTools.ttLib import TTFont

src, dst, font_path, face = sys.argv[1:5]
fs_type = TTFont(font_path)['OS/2'].fsType
if fs_type & 0x0002:
    sys.exit(f'font licence forbids embedding (fsType={fs_type})')

font_bytes = open(font_path, 'rb').read()
zin = zipfile.ZipFile(src)
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        name, data = info.filename, zin.read(info.filename)
        if name == '[Content_Types].xml':
            s = data.decode()
            if 'Extension="fntdata"' not in s:
                s = s.replace('<Default Extension="xml"',
                              '<Default Extension="fntdata" ContentType="application/x-fontdata"/><Default Extension="xml"', 1)
            data = s.encode()
        elif name == 'ppt/_rels/presentation.xml.rels':
            data = data.decode().replace(
                '</Relationships>',
                '<Relationship Id="rIdFont1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" '
                'Target="fonts/font1.fntdata"/></Relationships>').encode()
        elif name == 'ppt/presentation.xml':
            s = data.decode().replace(' saveSubsetFonts="1"', '')
            s = s.replace('<p:presentation ', '<p:presentation embedTrueTypeFonts="1" ', 1)
            m = re.search(r'<p:notesSz [^>]*/>', s)  # embeddedFontLst must follow notesSz (schema order)
            if not m:
                sys.exit('unexpected presentation.xml: no <p:notesSz>')
            lst = (f'<p:embeddedFontLst><p:embeddedFont><p:font typeface="{face}" pitchFamily="2" charset="-122"/>'
                   '<p:regular r:id="rIdFont1"/></p:embeddedFont></p:embeddedFontLst>')
            data = (s[:m.end()] + lst + s[m.end():]).encode()
        elif re.fullmatch(r'ppt/slides/slide\d+\.xml', name):
            s = data.decode()
            s = re.sub(r'(name="fill-[^"]*".*?</a:custGeom><a:solidFill><a:srgbClr val="000000"/></a:solidFill>)<a:ln></a:ln>',
                       r'\1<a:ln><a:noFill/></a:ln>', s, flags=re.S)
            data = s.encode()
        zout.writestr(info, data)
    zout.writestr('ppt/fonts/font1.fntdata', font_bytes)
print(f'embedded {face} ({len(font_bytes)} bytes) -> {dst}')
