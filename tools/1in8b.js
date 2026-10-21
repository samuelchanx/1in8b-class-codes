/*
 * 1in8b.life class-code PRNG — exact replica of the game's seeding chain.
 *
 * The game seeds its RNG in classroom mode (startNewLife):
 *     setRng(seedRng('1in8b-class:' + code + ':' + YYYY + '-' + M + '-' + D))
 * where M and D are NOT zero-padded and the date is the browser's LOCAL date.
 *
 * seedRng = FNV-style string hash -> mulberry32. Draws:
 *     draw 1: country  (weighted by annual births, COUNTRIES order)
 *     draw 2: sex      (chance(srb): CHN 0.528 / IND 0.519 / else 0.512 -> male)
 *
 * Works in the browser (window.OneIn8B) and Node (module.exports).
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.OneIn8B = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var SRB = { CHN: 0.528, IND: 0.519 };
  var REGIONS = {
    hi: 'High income',
    eca: 'Europe & Central Asia',
    eap: 'East Asia & Pacific',
    sa: 'South Asia',
    ssa: 'Sub-Saharan Africa',
    mena: 'Middle East & N. Africa',
    lac: 'Latin America & Caribbean'
  };

  function seedRng(str) {
    var h = 1779033703 ^ str.length;
    for (var i = 0; i < str.length; i++) {
      h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
      h = (h << 13) | (h >>> 19);
    }
    var a = h >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t = (t + Math.imul(t ^ (t >>> 7), t | 61)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // Date parts as plain ints (no padding) — must match the game's key exactly.
  function dateKey(y, m, d) {
    return y + '-' + m + '-' + d;
  }

  function sexOf(id, rng) {
    return rng() < (SRB[id] || 0.512) ? 'M' : 'F';
  }

  /*
   * Scan all 10000 codes for one date.
   * countries: array of {id, b} (full records fine). Returns:
   *   { key, total, byCountry: {id: [{code, g}...]}, indPct, mean }
   */
  function scanDate(countries, y, m, d) {
    var key = dateKey(y, m, d);
    var total = 0, i, c;
    for (i = 0; i < countries.length; i++) total += Math.max(0, countries[i].b);
    var byCountry = {};
    for (i = 0; i < countries.length; i++) byCountry[countries[i].id] = [];
    var ind = 0, rsum = 0;
    for (var n = 0; n < 10000; n++) {
      var code = ('000' + n).slice(-4);
      var rng = seedRng('1in8b-class:' + code + ':' + key);
      var r = rng(); rsum += r;
      var x = r * total, pick = null;
      for (i = 0; i < countries.length; i++) {
        x -= Math.max(0, countries[i].b);
        if (x <= 0) { pick = countries[i]; break; }
      }
      if (!pick) pick = countries[countries.length - 1];
      if (pick.id === 'IND') ind++;
      byCountry[pick.id].push({ code: code, g: sexOf(pick.id, rng) });
    }
    return { key: key, total: total, byCountry: byCountry, indPct: ind / 100, mean: rsum / 10000 };
  }

  return { seedRng: seedRng, dateKey: dateKey, scanDate: scanDate, sexOf: sexOf, SRB: SRB, REGIONS: REGIONS };
});
