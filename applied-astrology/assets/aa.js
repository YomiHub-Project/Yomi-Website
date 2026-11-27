/* Yomi-Applied Astrology website – shared script: language switch (vi/en), mobile menu, back-to-top */
(function () {
  var KEY = 'aa_landing_lang';
  var html = document.documentElement;
  function setLang(l) { html.setAttribute('lang', l); try { localStorage.setItem(KEY, l); } catch (e) {} }
  try {
    var q = (location.search.match(/[?&]lang=(vi|en)\b/) || [])[1];
    var saved = q || localStorage.getItem(KEY);
    if (saved === 'vi' || saved === 'en') html.setAttribute('lang', saved);
  } catch (e) {}
  window.toggleLanguage = function () { setLang((html.getAttribute('lang') || 'vi') === 'vi' ? 'en' : 'vi'); };
  document.addEventListener('DOMContentLoaded', function () {
    var hd = document.querySelector('header'), bt = document.querySelector('.nav-toggle');
    if (hd && bt) bt.addEventListener('click', function () { var o = hd.classList.toggle('open'); bt.setAttribute('aria-expanded', o ? 'true' : 'false'); });
    var top = document.querySelector('.to-top');
    if (top) {
      window.addEventListener('scroll', function () { top.classList.toggle('show', window.scrollY > 600); }, { passive: true });
      top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
    }
  });
})();
