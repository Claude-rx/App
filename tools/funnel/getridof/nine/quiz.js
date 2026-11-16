/* Get Rid Of — the home-plan quiz on the first offer page, and the default choice on the smaller offer page.
 * It only chooses which of the page's SDK bundle cards is selected (a click on that card): the Campaign Cart SDK
 * owns the cards, the prices and the accept button. No personal data is read or stored: two answers and a pack count.
 * Plan sizes follow the brand's own guide: one pack (12 pouches) per zone. An apartment and a one-story house are 2
 * zones, a two-story house 4, a large home 5; a garage or shed adds one and a vehicle adds one. That gives the guide's
 * own examples: one-story house + garage = 3 packs, two-story house + garage = 5 packs. */
(function () {
  'use strict';
  function ss(k, v) { try { if (v === undefined) return sessionStorage.getItem(k); sessionStorage.setItem(k, v); } catch (e) { return null; } }
  function track(n, p) { if (typeof window.groTrack === 'function') window.groTrack(n, p); }
  function plural(n, w) { return n + ' ' + w + (n === 1 ? '' : 's'); }
  function ordered() { var m = /(\d+)$/.exec(ss('gro_bundle') || ''); var n = m ? parseInt(m[1], 10) : 1; return n >= 1 && n <= 8 ? n : 1; }
  function tierFor(gap) { if (gap <= 1) return 1; if (gap <= 3) return gap; return 5; }

  /* select a bundle card by id; the SDK attaches its click handler when it starts, so retry until the card reports it */
  function choose(id, mark) {
    var tries = 0;
    [].forEach.call(document.querySelectorAll('[data-next-bundle-card][data-gq-rec]'), function (c) { c.removeAttribute('data-gq-rec'); });
    (function go() {
      var card = document.querySelector('[data-next-bundle-card][data-next-bundle-id="' + id + '"]');
      if (card && mark) card.setAttribute('data-gq-rec', '');
      if (card && card.classList.contains('next-selected')) return;
      if (card) card.click();
      if (++tries < 40) setTimeout(go, 250);
    })();
  }

  /* one-time buyers have no refills: the add-on note speaks to them, not to subscribers */
  if (/^ot/.test(ss('gro_bundle') || '')) {
    [].forEach.call(document.querySelectorAll('.bullet-features-text-box > div'), function (d) {
      if (/refill schedule does not change/.test(d.textContent)) d.textContent = 'One-time add-on: nothing recurring, no subscription';
    });
  }

  /* the smaller offer page: default to the 5-pack when the quiz said the home needs it */
  if (document.querySelector('[data-next-selector-id="home-plan-last"]')) {
    var saved = parseInt(ss('gro_plan_tier') || '', 10);
    if (saved === 5) choose('home-plan-last-5', false);
    if (ss('gro_plan') === 'covered') {    // the quiz just told this buyer the order covers the home
      var h = document.querySelector('h1.display-lg'), p = h && h.parentNode.querySelector('p.text-xl'), mt = document.querySelector('.gro-map__title');
      if (h) h.textContent = 'Want a Spare Pack for Your Next Swap?';
      if (p) p.textContent = 'Your order already covers your home. Each pouch lasts up to 90 days, so a spare pack is ready when it is time to swap. Added to the order you just placed.';
      if (mt) mt.textContent = 'Where pouches go in a typical home';
      var mi = document.querySelector('.gro-map__intro'); if (mi) mi.textContent = 'Here is where pouches go in a typical home.';
      var c1 = document.querySelector('[data-next-bundle-id="home-plan-last-1"]'), c5 = document.querySelector('[data-next-bundle-id="home-plan-last-5"]');
      var hint = function (c, t) { var e = c && c.querySelector('.next-bundle-tier-card__hint'); if (e) e.textContent = t; };
      var lab = function (c, t) { var e = c && c.querySelector('.next-bundle-tier-card__label'); if (e) e.textContent = t; };
      hint(c1, '12 pouches · a spare for your next swap'); lab(c5, '5 spare packs'); hint(c5, '60 pouches · lowest price per pack');
      /* the rest of the page speaks to a spare too, not to a new room */
      [].forEach.call(document.querySelectorAll('h2.display-md'), function (h2) {
        if (!/Where one more pack goes/.test(h2.textContent)) return;
        h2.textContent = 'Where a spare pack goes';
        var t = h2.nextElementSibling;
        if (t) t.textContent = 'Keep it sealed and out of reach of children until swap day. Then put fresh pouches in the same spots: every way in, along the walls, and the places you rarely check.';
      });
      var see = document.querySelector('a[href="#gro-map"]'); if (see) see.textContent = 'See where pouches go ↓';
    }
    return;
  }

  var root = document.querySelector('[data-gro-quiz]');
  if (!root) return;
  var state = { base: 0, name: '', extra: 0 };
  function show(which) {
    [].forEach.call(root.querySelectorAll('[data-gq]'), function (el) { el.hidden = el.getAttribute('data-gq') !== which; });
    var step = root.querySelector('[data-gq-step]');
    step.textContent = which === '1' ? 'Question 1 of 2 · takes 20 seconds' : which === '2' ? 'Question 2 of 2' : 'Done';
    step.hidden = which === 'r';
  }
  function result() {
    var need = state.base + state.extra, have = ordered(), gap = need - have, t = tierFor(gap);
    root.querySelector('[data-gq-total]').textContent = plural(need, 'pack');
    root.querySelector('[data-gq-pouches]').textContent = need * 12;
    root.querySelector('[data-gq-ordered]').textContent = plural(have, 'pack');
    root.querySelector('[data-gq-have]').style.width = Math.max(8, Math.min(100, Math.round(have / need * 100))) + '%';
    var line = root.querySelector('[data-gq-line]'), wrap = root.querySelector('[data-gq-gapwrap]');
    if (gap > 0) {
      wrap.hidden = false;
      root.querySelector('[data-gq-gap]').textContent = plural(gap, 'pack');
      line.textContent = state.name.charAt(0).toUpperCase() + state.name.slice(1) + (state.extra === 1 ? ' with the extra you picked' : state.extra ? ' with the extras you picked' : '') + ' takes about ' + plural(need, 'pack') +
        ', one per zone. Your order covers ' + plural(have, 'zone') + ', so ' + (gap === 1 ? '1 is' : gap + ' are') + ' still open. ' +
        (t > gap ? 'We selected the 5-pack below: on this page it costs less than ' + gap + ' single packs.'
          : gap > t ? 'We selected the 5-pack below, the largest add-on on this page.' : 'We selected ' + plural(t, 'more pack') + ' below.');
    } else {
      wrap.hidden = true;
      var base = 'Good news: your order already covers this plan. You don’t need more today.' +
        (/^buy/.test(ss('gro_bundle') || '') ? ' Your refills keep the pouches fresh.' : ' Each pouch lasts up to 90 days.');
      var price = function () { var e = document.querySelector('[data-next-bundle-id="home-plan-1"] [data-next-bundle-display="price"]'); return e && /\$\d/.test(e.textContent) ? e.textContent.trim() : ''; };
      var say = function (p) { line.textContent = base + ' Want a spare for the next swap? ' + (p ? 'One pack is ' + p + ' below.' : 'The 1-pack price is below.') + ' Otherwise, tap No thanks.'; };
      var p0 = price(); say(p0);
      /* answered before the SDK priced the cards: fill the price in as soon as it arrives (only if this line is still showing) */
      if (!p0) (function wait(n) { var p = price(); if (p) { if (line.textContent.indexOf('The 1-pack price is below.') !== -1) say(p); return; } if (n < 80) setTimeout(function () { wait(n + 1); }, 250); })(0);
    }
    ss('gro_plan_tier', String(t));
    ss('gro_plan', gap > 0 ? 'open' : 'covered');
    show('r');
    root.querySelector('[data-gq-go]').textContent = gap > 0 ? 'See my plan and price ↓' : 'See the add-on prices ↓';
    choose('home-plan-' + t, gap > 0);
    track('quiz_done', { home: state.name, extra: state.extra, need: need, ordered: have, tier: t });
  }
  root.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('button,[data-gq-go]');
    if (!b || !root.contains(b)) return;
    if (b.hasAttribute('data-gq-home')) {
      state.base = parseInt(b.getAttribute('data-gq-home'), 10); state.name = b.getAttribute('data-gq-name');
      track('quiz_home', { home: state.name }); show('2');
    } else if (b.hasAttribute('data-gq-extra')) {
      state.extra = parseInt(b.getAttribute('data-gq-extra'), 10); result();
    } else if (b.hasAttribute('data-gq-again')) {
      show('1');
    } else if (b.hasAttribute('data-gq-go')) {
      e.preventDefault();
      var plan = document.querySelector('#gro-plan .next-bundle-tier-grid') || document.getElementById('gro-plan');
      if (plan) plan.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
})();
