# Yomi-Website

Website chính thức của **YomiHub** – ứng dụng đọc truyện tranh, tiểu thuyết và xem phim/anime (Android, Android TV, Windows).

🌐 **https://yomihub-project.github.io/Yomi-Website/**

| Trang | GitHub – Tiếng Việt | GitHub – English | WordPress – Tiếng Việt | WordPress – English |
|---|---|---|---|---|
| Trang Chủ | [index.html](https://yomihub-project.github.io/Yomi-Website/index.html) | [en/index.html](https://yomihub-project.github.io/Yomi-Website/en/index.html) | [https://yomihubproject.wordpress.com/](https://yomihubproject.wordpress.com/) | [https://yomihubproject.wordpress.com/en/](https://yomihubproject.wordpress.com/en/) |
| Tải Về | [download.html](https://yomihub-project.github.io/Yomi-Website/download.html) | [en/download.html](https://yomihub-project.github.io/Yomi-Website/en/download.html) | [https://yomihubproject.wordpress.com/tai-ve/](https://yomihubproject.wordpress.com/tai-ve/) | [https://yomihubproject.wordpress.com/en-download/](https://yomihubproject.wordpress.com/en-download/) |
| Hướng Dẫn | [guide.html](https://yomihub-project.github.io/Yomi-Website/guide.html) | [en/guide.html](https://yomihub-project.github.io/Yomi-Website/en/guide.html) | [https://yomihubproject.wordpress.com/huong-dan/](https://yomihubproject.wordpress.com/huong-dan/) | [https://yomihubproject.wordpress.com/en-guide/](https://yomihubproject.wordpress.com/en-guide/) |
| Chính Sách Quyền Riêng Tư | [privacy.html](https://yomihub-project.github.io/Yomi-Website/privacy.html) | [en/privacy.html](https://yomihub-project.github.io/Yomi-Website/en/privacy.html) | [https://yomihubproject.wordpress.com/chinh-sach-quyen-rieng-tu/](https://yomihubproject.wordpress.com/chinh-sach-quyen-rieng-tu/) | [https://yomihubproject.wordpress.com/en-privacy/](https://yomihubproject.wordpress.com/en-privacy/) |

- Mã nguồn ứng dụng & bản cài: https://github.com/YomiHub-Project/YomiHub-Project (mục **Releases**).
- Trang Tải Về tự lấy liên kết bản mới nhất từ GitHub Releases.
- Website tĩnh (HTML/CSS/JS), phông Be Vietnam Pro tự lưu trữ (`assets/fonts`, giấy phép OFL), không tải tài nguyên từ máy chủ ngoài.
- **WordPress** (site https://yomihubproject.wordpress.com, mẫu *Blank*): nội dung sinh bằng `python3 tools/wp_inline.py . wp-export`.
- Chuyển từ thư mục `docs/` của repo YomiHub-Project ngày 26/11/2026; địa chỉ cũ `yomihub-project.github.io/YomiHub-Project/` tự chuyển hướng về đây.

## Yomi-Tử Vi Ứng Dụng (Yomi-Applied Astrology)

Website của app Tử Vi nằm trong thư mục [`applied-astrology/`](applied-astrology/) (song ngữ Việt/Anh trong cùng trang, nút đổi ngôn ngữ).

🌐 **https://yomihub-project.github.io/Yomi-Website/applied-astrology/**

| Trang | GitHub (Việt/Anh, nút đổi ngôn ngữ) | WordPress – Tiếng Việt | WordPress – English |
|---|---|---|---|
| Trang Chủ | [applied-astrology/index.html](https://yomihub-project.github.io/Yomi-Website/applied-astrology/index.html) | [https://yomihubproject.wordpress.com/tu-vi-ung-dung/](https://yomihubproject.wordpress.com/tu-vi-ung-dung/) | [https://yomihubproject.wordpress.com/applied-astrology/](https://yomihubproject.wordpress.com/applied-astrology/) |
| Tải Xuống | [applied-astrology/download.html](https://yomihub-project.github.io/Yomi-Website/applied-astrology/download.html) | [https://yomihubproject.wordpress.com/tu-vi-ung-dung/tai-xuong/](https://yomihubproject.wordpress.com/tu-vi-ung-dung/tai-xuong/) | [https://yomihubproject.wordpress.com/applied-astrology/download/](https://yomihubproject.wordpress.com/applied-astrology/download/) |
| Hướng Dẫn Sử Dụng | [applied-astrology/guide.html](https://yomihub-project.github.io/Yomi-Website/applied-astrology/guide.html) | [https://yomihubproject.wordpress.com/tu-vi-ung-dung/huong-dan/](https://yomihubproject.wordpress.com/tu-vi-ung-dung/huong-dan/) | [https://yomihubproject.wordpress.com/applied-astrology/guide/](https://yomihubproject.wordpress.com/applied-astrology/guide/) |
| Chính Sách Quyền Riêng Tư | [applied-astrology/privacy.html](https://yomihub-project.github.io/Yomi-Website/applied-astrology/privacy.html) | [https://yomihubproject.wordpress.com/tu-vi-ung-dung/chinh-sach-quyen-rieng-tu/](https://yomihubproject.wordpress.com/tu-vi-ung-dung/chinh-sach-quyen-rieng-tu/) | [https://yomihubproject.wordpress.com/applied-astrology/privacy/](https://yomihubproject.wordpress.com/applied-astrology/privacy/) |

- Mã nguồn & bản cài: https://github.com/YomiHub-Project/Applied-Astrology-T-Vi- (mục **Releases**).
- Mỗi bản phát hành: cập nhật phiên bản, tên tệp, dung lượng, bản cũ trong `applied-astrology/download.html` (12 link `releases/download/v<ver>/…`).
- CSS/JS dùng chung: `applied-astrology/assets/aa.css`, `aa.js`; không tải tài nguyên từ máy chủ ngoài.
- **WordPress** (mẫu *Blank*, link ở bảng trên): nội dung sinh bằng `python3 tools/wp_inline_aa.py . wp-export/applied-astrology` (style nội tuyến, tách Việt/Anh – nút English/Tiếng Việt chuyển giữa 2 bản, không liên kết về YomiHub; chữ gradient đổi sang màu đặc vì WordPress.com lọc `background-clip`). Sửa trang GitHub ⇒ chạy lại lệnh này rồi cập nhật 8 trang WordPress.
- Chuyển từ thư mục `docs/` của repo Applied-Astrology-T-Vi- ngày 27/11/2026; địa chỉ cũ `yomihub-project.github.io/Applied-Astrology-T-Vi-/` tự chuyển hướng về đây.

## Yomi-Office Open Source

Website của bộ ứng dụng văn phòng Yomi-Office Open Source nằm trong thư mục [`yomi-office/`](yomi-office/) — bản tiếng Việt ở `yomi-office/*.html`, bản tiếng Anh ở `yomi-office/en/*.html`; nút **English / Tiếng Việt** chuyển sang cùng trang ở ngôn ngữ kia.

🌐 **https://yomihub-project.github.io/Yomi-Website/yomi-office/**

| Trang | GitHub – Tiếng Việt | GitHub – English | WordPress – Tiếng Việt | WordPress – English |
|---|---|---|---|---|
| Trang Chủ | [index.html](https://yomihub-project.github.io/Yomi-Website/yomi-office/index.html) | [en/index.html](https://yomihub-project.github.io/Yomi-Website/yomi-office/en/index.html) | [https://yomihubproject.wordpress.com/yomi-office/](https://yomihubproject.wordpress.com/yomi-office/) | [https://yomihubproject.wordpress.com/yomi-office-en/](https://yomihubproject.wordpress.com/yomi-office-en/) |
| Tải Xuống | [download.html](https://yomihub-project.github.io/Yomi-Website/yomi-office/download.html) | [en/download.html](https://yomihub-project.github.io/Yomi-Website/yomi-office/en/download.html) | [https://yomihubproject.wordpress.com/yomi-office/tai-xuong/](https://yomihubproject.wordpress.com/yomi-office/tai-xuong/) | [https://yomihubproject.wordpress.com/yomi-office-en/download/](https://yomihubproject.wordpress.com/yomi-office-en/download/) |
| Hướng Dẫn Sử Dụng | [guide.html](https://yomihub-project.github.io/Yomi-Website/yomi-office/guide.html) | [en/guide.html](https://yomihub-project.github.io/Yomi-Website/yomi-office/en/guide.html) | [https://yomihubproject.wordpress.com/yomi-office/huong-dan/](https://yomihubproject.wordpress.com/yomi-office/huong-dan/) | [https://yomihubproject.wordpress.com/yomi-office-en/guide/](https://yomihubproject.wordpress.com/yomi-office-en/guide/) |
| Chính Sách Quyền Riêng Tư | [privacy.html](https://yomihub-project.github.io/Yomi-Website/yomi-office/privacy.html) | [en/privacy.html](https://yomihub-project.github.io/Yomi-Website/yomi-office/en/privacy.html) | [https://yomihubproject.wordpress.com/yomi-office/chinh-sach-quyen-rieng-tu/](https://yomihubproject.wordpress.com/yomi-office/chinh-sach-quyen-rieng-tu/) | [https://yomihubproject.wordpress.com/yomi-office-en/privacy/](https://yomihubproject.wordpress.com/yomi-office-en/privacy/) |

- Mã nguồn & bản cài: https://github.com/YomiHub-Project/Yomi-Office-Open-Source (mục **Releases**).
- Mỗi bản phát hành: cập nhật phiên bản, tên tệp, dung lượng trong `yomi-office/download.html` và `yomi-office/en/download.html` (link `releases/download/v<ver>/…`).
- CSS/JS dùng chung: `yomi-office/assets/office.css`, `office.js`; không tải tài nguyên từ máy chủ ngoài.
- **WordPress** (mẫu *Blank*): nội dung sinh bằng `python3 tools/wp_inline_office.py` (style nội tuyến, không JS, nút English/Tiếng Việt chuyển giữa 2 bản, không liên kết về YomiHub) → `wp-export/yomi-office/`. Sửa trang GitHub ⇒ chạy lại lệnh này rồi cập nhật 8 trang WordPress.
- 8 trang WordPress được tạo bằng cách **nhập tệp WXR** `wp-export/yomi-office/yomi-office-wordpress-import.xml` (trang cha `yomi-office` / `yomi-office-en`, mẫu *Blank*, mô tả SEO) qua WordPress.com MCP (`wpcom-content-import-*`) — trình duyệt tự động bị WordPress.com chặn bằng trang chống bot. Lần cập nhật sau: sửa nội dung từng trang (ID 9101–9104, 9111–9114) thay vì nhập lại để tránh tạo trùng.

## Hệ sinh thái Yomi-Project (`projects/` & `links/`)

Hai trang tổng quan và danh bạ liên kết chính thức cho hệ sinh thái 3 dự án mã nguồn mở **Yomi-Project** (YomiHub, Yomi-Tử Vi Ứng Dụng / Yomi-Applied Astrology, Yomi-Office Open Source). Song ngữ Việt/Anh ngay trong trang (mặc định Tiếng Việt, lưu lựa chọn vào `localStorage`, hỗ trợ `?lang=en` / `?lang=vi`).

🌐 **https://yomihub-project.github.io/Yomi-Website/projects/** · **https://yomihub-project.github.io/Yomi-Website/links/**

| Trang | GitHub Pages (song ngữ VI/EN) | WordPress – Tiếng Việt (dự kiến) | WordPress – English (planned) | Tệp xuất WordPress |
|---|---|---|---|---|
| Giới thiệu hệ sinh thái Yomi-Project | [projects/index.html](https://yomihub-project.github.io/Yomi-Website/projects/) | [https://yomihubproject.wordpress.com/yomi-project/](https://yomihubproject.wordpress.com/yomi-project/) | [https://yomihubproject.wordpress.com/yomi-project-en/](https://yomihubproject.wordpress.com/yomi-project-en/) | `wp-export/yomi-project/projects-vi.html`, `projects-en.html` |
| Danh bạ liên kết chính thức | [links/index.html](https://yomihub-project.github.io/Yomi-Website/links/) | [https://yomihubproject.wordpress.com/yomi-project/lien-ket/](https://yomihubproject.wordpress.com/yomi-project/lien-ket/) | [https://yomihubproject.wordpress.com/yomi-project-en/links/](https://yomihubproject.wordpress.com/yomi-project-en/links/) | `wp-export/yomi-project/links-vi.html`, `links-en.html` |

- CSS/JS dùng chung: kế thừa `assets/site.css` (phông Be Vietnam Pro tự lưu trữ) cùng `assets/yomi-project.css` và `assets/yomi-project.js`; không tải tài nguyên từ máy chủ ngoài, không dùng `<svg>` hay `background-clip: text` để đồng nhất giao diện với bản xuất WordPress.
- **WordPress** (mẫu *Blank*, style nội tuyến `<!-- wp:html -->`, tách Việt/Anh): nội dung sinh bằng `python3 tools/wp_inline_yp.py . wp-export/yomi-project` → `wp-export/yomi-project/` (`projects-vi.html`, `projects-en.html`, `links-vi.html`, `links-en.html`). Sửa trang GitHub ⇒ chạy lại lệnh này rồi cập nhật 4 trang WordPress.
