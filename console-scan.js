/* 1in8b.life class-code scanner — paste into the DevTools console (F12) on https://1in8b.life/
 *
 * Uses the site's OWN seedRng + COUNTRIES (top-level consts visible to console
 * evaluation; the site's CSP does not block DevTools console input), so there is
 * zero risk of port drift. Chrome may ask you to type "allow pasting" first.
 *
 * Draw 1 = country (births-weighted). Draw 2 = sex (chance(srb)).
 */
(() => {
  const DATE = '2026-10-21';   // the game seeds with the browser's LOCAL date, YYYY-M-D (no zero-padding)
  const WANT = 'HKG';          // any ISO3 id from COUNTRIES
  const srb = id => (id === 'CHN' ? 0.528 : id === 'IND' ? 0.519 : 0.512);
  const total = COUNTRIES.reduce((s, c) => s + Math.max(0, c.b), 0);
  const hits = []; let ind = 0;
  for (let i = 0; i < 10000; i++) {
    const code = String(i).padStart(4, '0');
    const rng = seedRng('1in8b-class:' + code + ':' + DATE);
    const r = rng();                                   // draw 1: country
    let x = r * total, pick = null;
    for (const c of COUNTRIES) { x -= Math.max(0, c.b); if (x <= 0) { pick = c; break; } }
    if (pick.id === 'IND') ind++;
    if (pick.id === WANT) hits.push(code + '(' + (rng() < srb(pick.id) ? 'M' : 'F') + ')');  // draw 2: sex
  }
  console.log('sanity: IND ' + (ind / 100).toFixed(1) + '% (want 17-19)');
  console.log(WANT + ' codes for ' + DATE + ':', hits.length ? hits.join(' ') : 'none today');
})();
