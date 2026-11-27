/* Yomi-Office Open Source website – menu thu gọn (mobile), nút về đầu trang, tự lấy bản phát hành mới nhất (trang Tải Xuống).
   Trang vẫn dùng được đầy đủ khi tắt JavaScript (bản WordPress không có JS). */
(function () {
  document.addEventListener('DOMContentLoaded', function () {
    var hd = document.querySelector('header'), bt = document.querySelector('.nav-toggle');
    if (hd && bt) bt.addEventListener('click', function () { var o = hd.classList.toggle('open'); bt.setAttribute('aria-expanded', o ? 'true' : 'false'); });
    var top = document.querySelector('.to-top');
    if (top) {
      window.addEventListener('scroll', function () { top.classList.toggle('show', window.scrollY > 600); }, { passive: true });
      top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
    }
    // [data-latest-version]: hiện số phiên bản mới nhất từ GitHub Releases (không bắt buộc — có sẵn giá trị tĩnh)
    var els = document.querySelectorAll('[data-latest-version]');
    if (els.length && window.fetch) {
      fetch('https://api.github.com/repos/YomiHub-Project/Yomi-Office-Open-Source/releases/latest').then(function (r) { return r.ok ? r.json() : null; }).then(function (j) {
        if (j && j.tag_name) Array.prototype.forEach.call(els, function (e) { e.textContent = j.tag_name; });
      }).catch(function () {});
    }
  });
})();
