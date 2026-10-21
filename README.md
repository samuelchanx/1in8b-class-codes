# 🎲 1in8b Class Code Finder

**[1in8b.life](https://1in8b.life)** is a browser life simulator: you're born as a random
someone somewhere random. But in **classroom mode** the game accepts a *class code*, and
that code makes the "random" birth fully deterministic:

> **same day + same code = the same baby** — same country, same sex, same family.

This repo exploits that: scan all 10,000 codes (`0000`–`9999`) for any date **offline** and
pick the one that births you (or your students) in the country you want.

**→ [Open the finder tool](https://samuelchanx.github.io/1in8b-class-codes/)** — pick a date,
search a country, click a code chip to copy it. Runs entirely in your browser, zero network calls.

## The trick

Starting a classroom life runs (`startNewLife`):

```js
setRng(seedRng('1in8b-class:' + CODE + ':' + YYYY + '-' + M + '-' + D))
```

Key facts:

- The date is **your browser's local date**, and month/day are **not zero-padded**
  (4 July 2026 → `2026-7-4`).
- `seedRng` is an FNV-style string hash feeding **mulberry32**, a tiny 32-bit seeded PRNG.
  Knowing the seed string = knowing every "random" draw in advance.
- **Draw 1** = country, weighted by annual births (India ≈ 17.6%, Hong Kong ≈ 0.03%).
- **Draw 2** = sex: `chance(srb)` with China `0.528` / India `0.519` / elsewhere `0.512` → male.

The birth lottery never touches the network — the only APIs the game has are community
posts, memorials, rooms and a stats beacon. So the entire scan is computable offline.

## Three ways to use it

| Way | Best for |
|---|---|
| [Web tool](https://samuelchanx.github.io/1in8b-class-codes/) | Everyone — pick country, click a code |
| `console-scan.js` | One-off check using the **site's own** RNG functions (zero port-drift risk). Paste into DevTools on 1in8b.life — CSP does not block console input |
| `python3 tools/scan.py [YYYY-MM-DD] [ISO3]` | Offline CLI / scripting |

## Using a code

1. Open `https://1in8b.life/en/?edu=1` (classroom mode).
2. Choose the class-code option, enter a code listed for **today's** date.
3. The birth certificate should match the chip you picked (country + sex).

Limitations:

- A code only works for **one calendar day** — your local midnight flips every code.
- That life must run to the end before you can class-code again (the game's `eduHold`).
- Small countries get ~0–4 codes per day; some days a country has none.
- This tool predicts **country + sex**. Name, family and city are also pinned by the code,
  but computing them needs deeper draws (they're deterministic too — PRs welcome).

## Verification

`tools/test_anchors.js` (run with `node tools/test_anchors.js`) asserts a week of
pre-computed Hong Kong codes, including sex:

```
2026-10-18 → 6101        2026-10-22 → 0736, 3528, 8980
2026-10-19 → 0543(F), 6307(M), 9227(M)        2026-10-23 → 0093, 8495
2026-10-20 → 2061, 2477, 3512, 6344           2026-10-24 → 1504, 4950, 7443
2026-10-21 → 3039(F)                          2026-10-25 → 0312, 6565, 9816
```

`6101` and `3039(F)` were additionally **played end-to-end on the live site** and produced
Hong Kong births of the expected sex. Every scan also self-checks: the India share must sit
around 17–19% per date (long-run ≈ 17.8%, official site claims 17.6%) and the RNG mean ≈ 0.5.

> ⚠️ **Porting warning:** mulberry32's last step is `t = (t + imul(t ^ t>>>7, 61|t)) ^ t`.
> Drop the final `^ t` in a Python port and everything still *looks* right — mean ≈ 0.5,
> plausible distribution — but every single code is wrong. Only anchor codes (or the
> in-page console snippet) catch it.

## Game updates

Validated across v0.7.60 → v0.7.76+ (including the single-file → loader+bundle refactor):
the seeding chain didn't change. After any future update:

```sh
python3 tools/extract_countries.py   # refresh country data from the new bundle
node tools/test_anchors.js           # anchors must still pass
python3 tools/scan.py                # sanity numbers must still hold
```

## Fair play

Fan-made research/education project, not affiliated with the game. The trick is built into
the game itself (classroom mode exists so a whole class can share one birth); this just
makes the outcome computable in advance. Please support the original game.
Country statistics in `data/` are UN-derived figures extracted from the public game bundle
for interoperability; the game's code and content remain © its author. Tool code: [MIT](LICENSE).
