#!/usr/bin/env python3
"""Regenerate data/countries.min.{js,json} from the live 1in8b.life bundle.

Run this after the game ships a new version, then re-check the sanity numbers
(IND share ~17-19%, mean ~0.5) before trusting any scanned codes:

    python3 tools/extract_countries.py && python3 tools/scan.py

stdlib only; no dependencies.
"""
import json
import re
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def extract_bundle_url(html: str) -> str:
    m = re.search(r'src="(/a/en\.[a-z0-9]+\.js)"', html) or re.search(r'"(/a/en\.[a-z0-9]+\.js)"', html)
    if not m:
        raise SystemExit('could not find the /a/en.<hash>.js bundle URL in the loader page')
    return 'https://1in8b.life' + m.group(1)


def raw_decode_after(s: str, marker: str):
    pos = s.index(marker) + len(marker)
    obj, _ = json.JSONDecoder().raw_decode(s[pos:])
    return obj


def main() -> None:
    html = fetch('https://1in8b.life/en/').decode('utf-8', errors='replace')
    bundle_url = extract_bundle_url(html)
    print('bundle:', bundle_url)
    bundle = fetch(bundle_url).decode('utf-8', errors='replace')

    countries = raw_decode_after(bundle, 'COUNTRIES = ')

    # English display names live in an ISO3 -> name object in the i18n section.
    i = bundle.find('"Hong Kong"')
    if i == -1:
        raise SystemExit('English names map not found — bundle layout may have changed')
    start = bundle.rfind('{', 0, i)
    depth = 0
    for j in range(start, len(bundle)):
        if bundle[j] == '{':
            depth += 1
        elif bundle[j] == '}':
            depth -= 1
            if depth == 0:
                break
    names, _ = json.JSONDecoder().raw_decode(bundle[start:j + 1])

    rows = []
    for c in countries:
        nm = names.get(c['id'], c['id']).strip()
        if nm.lower().startswith('the '):
            nm = nm[4:]
        rows.append({'id': c['id'], 'name': nm, 'p': c['p'], 'b': c['b'],
                     'pop': c['pop'], 'le': c['le'], 'ppp': c['ppp'],
                     'tfr': c['tfr'], 'urb': c['urb']})

    (ROOT / 'data' / 'countries.min.json').write_text(
        json.dumps(rows, ensure_ascii=False, separators=(',', ':')))
    js = ('// Country data extracted from the 1in8b.life bundle (UN-derived statistics).\n'
          '// Regenerate with: python3 tools/extract_countries.py\n'
          'var COUNTRIES_DATA = ' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ';\n'
          "if (typeof module === 'object' && module.exports) module.exports = COUNTRIES_DATA;\n")
    (ROOT / 'data' / 'countries.min.js').write_text(js)
    print(f'wrote {len(rows)} countries -> data/countries.min.{{js,json}}')


if __name__ == '__main__':
    main()
