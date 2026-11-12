/* Scroll reveals and the nav shadow. Without JS (or with reduced motion) everything is simply visible. */
(function () {
  var nav = document.querySelector('.nav');
  var onScroll = function () { nav.classList.toggle('scrolled', window.scrollY > 8); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  var items = document.querySelectorAll('[data-reveal]');
  if (!('IntersectionObserver' in window)) { items.forEach(function (el) { el.classList.add('shown'); }); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('shown'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
  items.forEach(function (el) { io.observe(el); });
})();
