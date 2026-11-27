/**
 * Yomi-Project Hub Script (projects/ & links/)
 * Handles in-page VI/EN language switching, localStorage persistence (safe try/catch),
 * optional ?lang=vi|en query parameter support, document title/meta synchronization,
 * button active/aria-pressed state, and localized href updates.
 */
(function () {
  var STORAGE_KEY = 'yomi-project-lang';
  var html = document.documentElement;

  function readStorage(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (_) {
      return null;
    }
  }

  function writeStorage(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (_) {}
  }

  function getQueryLang() {
    try {
      var match = (window.location.search || '').match(/[?&]lang=(vi|en)\b/i);
      return match ? match[1].toLowerCase() : null;
    } catch (_) {
      return null;
    }
  }

  function stripLangQueryParam() {
    try {
      if (!window.history || !window.history.replaceState) return;
      if (!/[?&]lang=/i.test(window.location.search || '')) return;
      var url = new URL(window.location.href);
      url.searchParams.delete('lang');
      window.history.replaceState(null, '', url.pathname + url.search + url.hash);
    } catch (_) {}
  }

  function resolveInitialLang() {
    var q = getQueryLang();
    if (q === 'vi' || q === 'en') {
      writeStorage(STORAGE_KEY, q);
      return q;
    }
    var saved = readStorage(STORAGE_KEY);
    if (saved === 'vi' || saved === 'en') {
      return saved;
    }
    return 'vi';
  }

  function syncDocumentMeta(lang) {
    var titleAttr = lang === 'en' ? 'data-title-en' : 'data-title-vi';
    var descAttr = lang === 'en' ? 'data-desc-en' : 'data-desc-vi';
    var nextTitle = html.getAttribute(titleAttr);
    if (nextTitle) {
      document.title = nextTitle;
    }
    var nextDesc = html.getAttribute(descAttr);
    if (nextDesc) {
      var metaDesc = document.querySelector('meta[name="description"]');
      if (metaDesc) {
        metaDesc.setAttribute('content', nextDesc);
      }
    }
  }

  function syncControls(lang) {
    var buttons = document.querySelectorAll('.lang-opt[data-switch-lang]');
    buttons.forEach(function (btn) {
      var isActive = btn.getAttribute('data-switch-lang') === lang;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });

    var localizedLinks = document.querySelectorAll('a[data-href-vi][data-href-en]');
    localizedLinks.forEach(function (link) {
      var target = link.getAttribute(lang === 'en' ? 'data-href-en' : 'data-href-vi');
      if (target) {
        link.setAttribute('href', target);
      }
    });
  }

  function applyLang(lang, persist, cleanUrl) {
    var normalized = lang === 'en' ? 'en' : 'vi';
    html.setAttribute('lang', normalized);
    if (persist) {
      writeStorage(STORAGE_KEY, normalized);
    }
    if (cleanUrl) {
      stripLangQueryParam();
    }
    syncDocumentMeta(normalized);
    syncControls(normalized);
  }

  // Apply immediately in <head> to prevent language flash on initial paint
  var initialLang = resolveInitialLang();
  html.setAttribute('lang', initialLang);

  window.setYomiLang = function (lang) {
    applyLang(lang, true, true);
  };

  window.toggleLanguage = function () {
    var current = (html.getAttribute('lang') || 'vi').toLowerCase();
    applyLang(current === 'vi' ? 'en' : 'vi', true, true);
  };

  document.addEventListener('DOMContentLoaded', function () {
    var currentLang = (html.getAttribute('lang') || 'vi').toLowerCase() === 'en' ? 'en' : 'vi';
    syncDocumentMeta(currentLang);
    syncControls(currentLang);

    var buttons = document.querySelectorAll('.lang-opt[data-switch-lang]');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var nextLang = btn.getAttribute('data-switch-lang');
        if (nextLang === 'vi' || nextLang === 'en') {
          applyLang(nextLang, true, true);
        }
      });
    });
  });
})();
