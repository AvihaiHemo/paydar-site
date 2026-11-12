/* Paydar free calculators. Money is integer cents, time is integer minutes. */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var num = function (id) {
    var el = $(id);
    if (!el) return 0;
    var v = parseFloat(String(el.value).replace(',', '.'));
    return isFinite(v) && v > 0 ? v : 0;
  };
  var cents = function (id) { return Math.round(num(id) * 100); };
  var money = function (c) {
    var neg = c < 0;
    c = Math.abs(Math.round(c));
    var s = (Math.floor(c / 100)).toLocaleString('en-US') + '.' + ('0' + (c % 100)).slice(-2);
    return (neg ? '-$' : '$') + s;
  };
  var hrs = function (min) { return (Math.round(min / 6) / 10).toFixed(1) + ' h'; };
  var hm = function (min) {
    var m = Math.abs(Math.round(min));
    return (min < 0 ? '-' : '') + Math.floor(m / 60) + ' h ' + ('0' + (m % 60)).slice(-2) + ' min';
  };
  var pay = function (rateCents, minutes, mult) { return Math.round(rateCents * minutes * mult / 60); };
  var set = function (id, text) { var el = $(id); if (el) el.textContent = text; };
  var show = function (id, on) { var el = $(id); if (el) el.hidden = !on; };
  var mins = function (v) {
    if (!v) return null;
    var p = v.split(':');
    return parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
  };
  var DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  /* Splits one workweek (7 daily minute totals) into regular / 1.5x / 2x minutes. */
  function splitWeek(day, rule) {
    var reg = 0, ot = 0, dt = 0;
    var allSeven = day.every(function (m) { return m > 0; });
    day.forEach(function (m, i) {
      if (rule === 'ca') {
        if (i === 6 && allSeven) { ot += Math.min(m, 480); dt += Math.max(m - 480, 0); return; }
        reg += Math.min(m, 480); ot += Math.min(Math.max(m - 480, 0), 240); dt += Math.max(m - 720, 0);
      } else if (rule === 'ak') {
        reg += Math.min(m, 480); ot += Math.max(m - 480, 0);
      } else if (rule === 'co') {
        reg += Math.min(m, 720); ot += Math.max(m - 720, 0);
      } else {
        reg += m;
      }
    });
    var weekly = Math.max(reg - 2400, 0);
    return { reg: reg - weekly, ot: ot + weekly, dt: dt };
  }

  function dayInputs(prefix) {
    return DAYS.map(function (_, i) { return Math.round(num(prefix + i) * 60); });
  }

  var tools = {
    overtime: function () {
      var rate = cents('rate');
      var s = splitWeek(dayInputs('d'), $('rule').value);
      var regPay = pay(rate, s.reg, 1), otPay = pay(rate, s.ot, 1.5), dtPay = pay(rate, s.dt, 2);
      set('o-reg', hrs(s.reg) + ' · ' + money(regPay));
      set('o-ot', hrs(s.ot) + ' · ' + money(otPay));
      set('o-dt', hrs(s.dt) + ' · ' + money(dtPay));
      show('row-dt', s.dt > 0);
      set('o-total', money(regPay + otPay + dtPay));
      set('o-premium', money(pay(rate, s.ot, 0.5) + pay(rate, s.dt, 1)));
    },

    timecard: function () {
      var total = 0;
      DAYS.forEach(function (_, i) {
        var a = mins($('in' + i).value), b = mins($('out' + i).value);
        var m = 0;
        if (a !== null && b !== null) {
          m = b - a; if (m < 0) m += 1440;
          m = Math.max(m - Math.round(num('br' + i)), 0);
        }
        set('t' + i, m ? hm(m) : '–');
        total += m;
      });
      var rate = cents('rate');
      set('o-hm', hm(total));
      set('o-dec', (Math.round(total / 0.6) / 100).toFixed(2) + ' h');
      var over = Math.max(total - 2400, 0);
      set('o-ot', hm(over));
      set('o-total', money(pay(rate, total - over, 1) + pay(rate, over, 1.5)));
    },

    paycheck: function () {
      var rate = cents('rate');
      var w1 = Math.round(num('w1') * 60), w2 = Math.round(num('w2') * 60);
      var expected = 0, otMin = 0;
      [w1, w2].forEach(function (w) {
        var over = Math.max(w - 2400, 0);
        otMin += over;
        expected += pay(rate, w - over, 1) + pay(rate, over, 1.5);
      });
      expected += cents('tips');
      var paid = cents('paid');
      var gap = expected - paid;
      set('o-expected', money(expected));
      set('o-ot', hrs(otMin));
      set('o-paid', money(paid));
      var box = $('verdict');
      if (!paid || !expected) { box.hidden = true; return; }
      box.hidden = false;
      box.className = 'verdict ' + (gap > 100 ? 'short' : 'ok');
      set('o-gap', gap > 100 ? money(gap) + ' may be missing'
        : gap < -100 ? 'You were paid ' + money(-gap) + ' more than expected'
        : 'Your paycheck matches');
      set('o-gap-note', gap > 100
        ? 'That is about ' + hm(Math.round(gap * 60 / Math.max(rate, 1))) + ' of work at your regular rate. Check the hours and the overtime line on your stub.'
        : gap < -100 ? 'Look for a bonus, a differential or paid time off on your stub.'
        : 'Gross pay on your stub is within $1 of what your hours come to.');
    },

    rounding: function () {
      var step = parseInt($('step').value, 10);
      var a = mins($('in').value), b = mins($('out').value);
      if (a === null || b === null) return;
      var round = function (m) { return Math.round(m / step) * step; };
      var actual = b - a; if (actual < 0) actual += 1440;
      var ra = round(a), rb = round(b);
      var rounded = rb - ra; if (rounded < 0) rounded += 1440;
      var diff = rounded - actual;
      var rate = cents('rate'), shifts = num('shifts') || 5;
      var fmt = function (m) { m = ((m % 1440) + 1440) % 1440; var h = Math.floor(m / 60); return ((h + 11) % 12 + 1) + ':' + ('0' + (m % 60)).slice(-2) + (h < 12 ? ' AM' : ' PM'); };
      set('o-rin', fmt(ra)); set('o-rout', fmt(rb));
      set('o-actual', hm(actual)); set('o-rounded', hm(rounded));
      set('o-diff', diff === 0 ? 'No change' : (diff > 0 ? '+' : '−') + Math.abs(diff) + ' min ' + (diff > 0 ? 'in your favor' : 'unpaid'));
      var perShift = pay(rate, Math.abs(diff), 1);
      set('o-shift', (diff < 0 ? '−' : diff > 0 ? '+' : '') + money(perShift));
      set('o-year', (diff < 0 ? '−' : diff > 0 ? '+' : '') + money(Math.round(perShift * shifts * 52)));
      $('verdict').className = 'verdict ' + (diff < 0 ? 'short' : 'ok');
    },

    tipout: function () {
      var tips = cents('tips'), sales = cents('sales'), total = 0;
      ['a', 'b', 'c'].forEach(function (k) {
        var pct = num('pct-' + k), base = $('base-' + k).value === 'sales' ? sales : tips;
        var c = Math.round(base * pct / 100);
        set('o-' + k, money(c));
        total += c;
      });
      var keep = tips - total, wage = pay(cents('rate'), Math.round(num('hours') * 60), 1);
      var m = Math.round(num('hours') * 60);
      set('o-out', money(total));
      set('o-keep', money(keep));
      set('o-wage', money(wage));
      set('o-total', money(keep + wage));
      set('o-hourly', m ? money(Math.round((keep + wage) * 60 / m)) + ' / h' : '–');
    },

    nanny: function () {
      var rate = cents('rate');
      var g = Math.round(num('guaranteed') * 60), w = Math.round(num('worked') * 60);
      var paidMin = Math.max(g, w);
      var over = $('livein').checked ? 0 : Math.max(w - 2400, 0);
      var base = pay(rate, paidMin - over, 1), ot = pay(rate, over, 1.5);
      set('o-paidhours', hrs(paidMin));
      set('o-topup', w < g ? hrs(g - w) + ' · ' + money(pay(rate, g - w, 1)) : 'None');
      set('o-ot', hrs(over) + ' · ' + money(ot));
      set('o-total', money(base + ot));
      set('o-year', money((base + ot) * 52));
    }
  };

  var form = document.querySelector('form[data-tool]');
  if (!form) return;
  var run = tools[form.getAttribute('data-tool')];
  form.addEventListener('input', run);
  form.addEventListener('submit', function (e) { e.preventDefault(); });
  run();
})();
