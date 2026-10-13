#!/usr/bin/env python3
"""Download a Google Fonts family as a single TTF (needed for metrics, embedding and the PDF).

usage: fetch_font.py "ZCOOL KuaiLe" fonts/
Prints the path of the downloaded file.
"""
import os
import re
import sys
import urllib.parse
import urllib.request

family, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
css_url = 'https://fonts.googleapis.com/css2?family=' + urllib.parse.quote_plus(family)
# An old user agent makes Google Fonts serve one complete TTF instead of woff2 subsets.
req = urllib.request.Request(css_url, headers={'User-Agent': 'Mozilla/4.0'})
css = urllib.request.urlopen(req).read().decode()
m = re.search(r'url\((https://[^)]+\.ttf)\)', css)
if not m:
    sys.exit('no TTF url found in Google Fonts CSS:\n' + css[:500])
path = os.path.join(out_dir, family.replace(' ', '') + '.ttf')
urllib.request.urlretrieve(m.group(1), path)
print(path)
