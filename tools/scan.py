#!/usr/bin/env python3
"""1in8b.life class-code scanner (offline, no network).

Usage:
    python3 tools/scan.py                      # today, all countries
    python3 tools/scan.py 2026-10-21           # a specific date (local-date semantics)
    python3 tools/scan.py 2026-10-21 HKG       # one country

The game seeds its classroom RNG with '1in8b-class:' + code + ':' + YYYY-M-D
(month/day NOT zero-padded, browser local date). seedRng = FNV-style hash +
mulberry32. Draw 1 picks the country (births-weighted), draw 2 the sex.

WARNING for anyone porting this further: mulberry32's last step is
    t = (t + Math.imul(t ^ t>>>7, 61|t)) ^ t
The final `^ t` is easy to drop in a Python port — the mean stays ~0.5 and the
distribution looks plausible, but every code comes out wrong. Validate with the
anchor codes in tools/test_anchors.js or the in-page console snippet.
"""
import json
import sys
from datetime import date as _date
from pathlib import Path

M = 0xFFFFFFFF
HERE = Path(__file__).resolve().parent


def seed_a(seed: str) -> int:
    h = (1779033703 ^ len(seed)) & M
    for ch in seed:
        h = ((h ^ ord(ch)) * 3432918353) & M
        h = ((h << 13) & M) | (h >> 19)
    return h


def make_rng(a: int):
    state = a & M

    def rng() -> float:
        nonlocal state
        state = (state + 0x6D2B79F5) & M
        t = ((state ^ (state >> 15)) * ((1 | state) & M)) & M
        t = ((t + ((t ^ (t >> 7)) * ((61 | t) & M) & M)) & M) ^ t
        return ((t ^ (t >> 14)) & M) / 4294967296

    return rng


def srb(cid: str) -> float:
    return 0.528 if cid == 'CHN' else 0.519 if cid == 'IND' else 0.512


def sex(cid: str, rng) -> str:
    return 'M' if rng() < srb(cid) else 'F'


def scan(countries, y: int, m: int, d: int):
    key = f'{y}-{m}-{d}'
    total = sum(max(0, c['b']) for c in countries)
    out = {c['id']: [] for c in countries}
    ind = 0
    rs = 0.0
    for n in range(10000):
        code = f'{n:04d}'
        rng = make_rng(seed_a(f'1in8b-class:{code}:{key}'))
        r = rng()
        rs += r
        x = r * total
        for c in countries:
            x -= max(0, c['b'])
            if x <= 0:
                if c['id'] == 'IND':
                    ind += 1
                out[c['id']].append((code, sex(c['id'], rng)))
                break
    return out, total, ind / 100, rs / 10000


def main() -> None:
    argv = sys.argv[1:]
    today = _date.today()
    y, m, d = (today.year, today.month, today.day)
    if argv:
        y, m, d = (int(p) for p in argv[0].split('-'))
    want = argv[1].upper() if len(argv) > 1 else None

    countries = json.loads((HERE.parent / 'data' / 'countries.min.json').read_text())
    names = {c['id']: c['name'] for c in countries}
    by_country, total, ind_pct, mean = scan(countries, y, m, d)

    print(f'Date {y}-{m}-{d}  |  sanity: IND {ind_pct:.1f}% (want 17-19), mean {mean:.3f} (want ~0.5)')
    targets = [want] if want else [c['id'] for c in countries]
    for cid in targets:
        hits = by_country.get(cid, [])
        label = f'{names.get(cid, cid)} ({cid})'
        if not hits:
            print(f'  {label}: no code today')
        else:
            odds = round(total / next(c["b"] for c in countries if c["id"] == cid))
            joined = ' '.join(f'{code}({g})' for code, g in hits)
            print(f'  {label}: {len(hits)} code(s), 1 in {odds} births — {joined}')


if __name__ == '__main__':
    main()
