#!/usr/bin/env python3
"""Compare the design render with the render rebuilt from the PPTX, and make contact sheets.

usage: compare.py design_shots/ pptx_shots/ [threshold_percent]
Exits 1 if any slide differs by more than the threshold (default 0.5% of pixels).
Writes sheetN.png (4 slides per sheet) into design_shots/ for visual review.
"""
import glob
import os
import sys

from PIL import Image, ImageChops

design, rebuilt = sys.argv[1], sys.argv[2]
threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
files = sorted(glob.glob(os.path.join(design, 's[0-9]*.png')))
bad = 0
for f in files:
    g = os.path.join(rebuilt, os.path.basename(f))
    if not os.path.exists(g):
        print(f'{os.path.basename(f)}: missing in {rebuilt}')
        bad += 1
        continue
    a, b = Image.open(f).convert('L'), Image.open(g).convert('L')
    diff = ImageChops.difference(a, b).point(lambda v: 255 if v > 100 else 0)
    pct = diff.histogram()[255] / (a.size[0] * a.size[1]) * 100
    flag = '  <-- check' if pct > threshold else ''
    bad += bool(flag)
    print(f'{os.path.basename(f)}: {pct:.3f}% pixels differ{flag}')

for k in range(0, len(files), 4):
    sheet = Image.new('RGB', (2 * 960 + 30, 2 * 540 + 30), (150, 150, 150))
    for j, f in enumerate(files[k:k + 4]):
        sheet.paste(Image.open(f).convert('RGB').resize((960, 540)), (10 + (j % 2) * 970, 10 + (j // 2) * 550))
    sheet.save(os.path.join(design, f'sheet{k // 4 + 1}.png'))
print(f'contact sheets -> {design}/sheet*.png')
sys.exit(1 if bad else 0)
