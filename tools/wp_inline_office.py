"""Convert Yomi-Office Open Source GitHub Pages HTML into inline-styled WordPress
Custom HTML blocks (light theme, zero <script>, no YomiHub link).

Reads from yomi-office/*.html and yomi-office/en/*.html, resolves all CSS rules
from yomi-office/assets/office.css into inline styles, expands .steps counters
into explicit badges, rewrites internal & language-switcher links to WordPress
slugs, strips YomiHub footer link, and writes 8 files into wp-export/yomi-office/.
"""
import os
import re
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "yomi-office")
OUT = os.path.join(ROOT, "wp-export", "yomi-office")
ASSET_BASE = "https://yomihub-project.github.io/Yomi-Website/yomi-office/assets/"

PAGES = [
    ("index.html", "vi", "index", "vi_index.html"),
    ("download.html", "vi", "download", "vi_download.html"),
    ("guide.html", "vi", "guide", "vi_guide.html"),
    ("privacy.html", "vi", "privacy", "vi_privacy.html"),
    ("en/index.html", "en", "index", "en_index.html"),
    ("en/download.html", "en", "download", "en_download.html"),
    ("en/guide.html", "en", "guide", "en_guide.html"),
    ("en/privacy.html", "en", "privacy", "en_privacy.html"),
]

WP = {
    "vi": {
        "index": "https://yomihubproject.wordpress.com/yomi-office/",
        "download": "https://yomihubproject.wordpress.com/yomi-office/tai-xuong/",
        "guide": "https://yomihubproject.wordpress.com/yomi-office/huong-dan/",
        "privacy": "https://yomihubproject.wordpress.com/yomi-office/chinh-sach-quyen-rieng-tu/",
    },
    "en": {
        "index": "https://yomihubproject.wordpress.com/yomi-office-en/",
        "download": "https://yomihubproject.wordpress.com/yomi-office-en/download/",
        "guide": "https://yomihubproject.wordpress.com/yomi-office-en/guide/",
        "privacy": "https://yomihubproject.wordpress.com/yomi-office-en/privacy/",
    },
}

VARS = {
    "--c1": "#1e40af",
    "--c2": "#2563eb",
    "--c3": "#06b6d4",
    "--ink": "#0f172a",
    "--sub": "#475569",
    "--mut": "#64748b",
    "--line": "#e2e8f0",
    "--bg": "#f5f7fb",
    "--card": "#ffffff",
    "--soft": "#eff6ff",
    "--ok": "#059669",
    "--warn": "#b45309",
    "--radius": "14px",
}

FONT = '"Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif'
VOID = {"meta", "link", "br", "hr", "img", "input", "col", "source"}
RAW_TAGS = {"script", "style", "button"}


class El:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.parent = parent
        self.children = []

    @property
    def classes(self):
        return self.attrs.get("class", "").split()

    @property
    def id(self):
        return self.attrs.get("id", "")


class Text:
    def __init__(self, data, parent=None):
        self.data = data
        self.parent = parent


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = El("root")
        self.cur = self.root
        self.skip_depth = 0
        self.skip_tag = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if self.skip_depth > 0:
            if tag == self.skip_tag:
                self.skip_depth += 1
            return
        if tag in RAW_TAGS:
            self.skip_tag = tag
            self.skip_depth = 1
            return
        el = El(tag, attrs, self.cur)
        self.cur.children.append(el)
        if tag not in VOID:
            self.cur = el

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.skip_depth > 0:
            if tag == self.skip_tag:
                self.skip_depth -= 1
                if self.skip_depth == 0:
                    self.skip_tag = None
            return
        if tag in VOID:
            return
        p = self.cur
        while p is not None and p.tag != tag:
            p = p.parent
        if p is not None and p.parent is not None:
            self.cur = p.parent

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.cur.children.append(Text(data, self.cur))

    def handle_entityref(self, name):
        if self.skip_depth == 0:
            self.cur.children.append(Text(f"&{name};", self.cur))

    def handle_charref(self, name):
        if self.skip_depth == 0:
            self.cur.children.append(Text(f"&#{name};", self.cur))


def resolve_vars(decl):
    out = decl
    for _ in range(3):
        out = re.sub(r"var\((--[a-zA-Z0-9-]+)\)", lambda m: VARS.get(m.group(1), m.group(0)), out)
    return out.strip()


def parse_css(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    out = []
    i = 0
    while i < len(text):
        m = re.match(r"\s*(@[^{]+)\{", text[i:])
        if m and m.group(1).strip().startswith("@"):
            j = i + len(m.group(0))
            depth = 1
            while j < len(text) and depth > 0:
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                j += 1
            i = j
            continue
        brace = text.find("{", i)
        if brace == -1:
            break
        sel = text[i:brace].strip()
        end = text.find("}", brace)
        body = text[brace + 1 : end].strip()
        i = end + 1
        if not sel or sel.startswith((":root", "*", "html")):
            continue
        for s in sel.split(","):
            s = s.strip()
            if not s or any(p in s for p in (":hover", "::before", "::after", ".open", ".show")):
                continue
            out.append((s, resolve_vars(body)))
    return out


def match_atom(el, atom):
    if atom == "*":
        return True
    m = re.match(r"^([a-zA-Z0-9_-]*)(.*)$", atom)
    tag_req, rest = m.group(1), m.group(2)
    if tag_req and el.tag != tag_req.lower():
        return False
    for am in re.finditer(r"\[([a-zA-Z0-9_-]+)=[\"']?([^\"'\]]+)[\"']?\]", rest):
        if el.attrs.get(am.group(1)) != am.group(2):
            return False
    rest = re.sub(r"\[[^\]]+\]", "", rest)
    for pseudo in re.findall(r":([a-zA-Z0-9_-]+)", rest):
        if pseudo == "last-child":
            sibs = [c for c in el.parent.children if isinstance(c, El)]
            if not sibs or sibs[-1] is not el:
                return False
        else:
            return False
    rest = re.sub(r":[a-zA-Z0-9_-]+", "", rest)
    for cid in re.findall(r"#([a-zA-Z0-9_-]+)", rest):
        if el.id != cid:
            return False
    for cls in re.findall(r"\.([a-zA-Z0-9_-]+)", rest):
        if cls not in el.classes:
            return False
    return True


def match_sel(el, sel):
    parts = re.split(r"\s*>\s*", sel.strip())
    if len(parts) > 1:
        if not match_sel(el, parts[-1]):
            return False
        cur = el
        for p in reversed(parts[:-1]):
            cur = cur.parent
            if cur is None or cur.tag == "root" or not match_sel(cur, p):
                return False
        return True
    atoms = sel.strip().split()
    if not atoms or not match_atom(el, atoms[-1]):
        return False
    cur = el.parent
    for atom in reversed(atoms[:-1]):
        while cur is not None and cur.tag != "root" and not match_atom(cur, atom):
            cur = cur.parent
        if cur is None or cur.tag == "root":
            return False
        cur = cur.parent
    return True


def spec(sel):
    s = re.sub(r"\[[^\]]+\]", ".x", sel)
    ids = len(re.findall(r"#[a-zA-Z0-9_-]+", s))
    clss = len(re.findall(r"\.[a-zA-Z0-9_-]+|:[a-zA-Z0-9_-]+", s))
    s_no = re.sub(r"[#.][a-zA-Z0-9_-]+|:[a-zA-Z0-9_-]+", "", s)
    tags = len(re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]*\b", s_no))
    return (ids, clss, tags)


def parse_decls(body):
    out = {}
    for part in body.split(";"):
        part = part.strip()
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        out[k.strip().lower()] = v.strip()
    return out


def dict_to_style(d):
    return ";".join(f"{k}:{v}" for k, v in d.items() if v)


def rewrite_href(href, lang):
    if not href or href.startswith(("http://", "https://", "mailto:", "#")):
        return href
    path, _, frag = href.partition("#")
    frag = ("#" + frag) if frag else ""
    if lang == "vi":
        for k in ("index", "download", "guide", "privacy"):
            if path == f"{k}.html":
                return WP["vi"][k] + frag
            if path == f"en/{k}.html":
                return WP["en"][k] + frag
    else:
        for k in ("index", "download", "guide", "privacy"):
            if path == f"{k}.html":
                return WP["en"][k] + frag
            if path == f"../{k}.html":
                return WP["vi"][k] + frag
    return href


def clean_for_wp(el, lang):
    if el.tag == "footer":
        # Remove YomiHub link from footer nav (WordPress policy: no YomiHub link)
        def strip_yh(node):
            kept = []
            for ch in node.children:
                if isinstance(ch, El):
                    if ch.tag == "a" and ch.attrs.get("href", "").endswith("index.html") and (
                        ".." in ch.attrs.get("href", "") and "YomiHub" in serialize_text(ch)
                    ):
                        continue
                    strip_yh(ch)
                kept.append(ch)
            node.children = kept
        strip_yh(el)

    if el.tag == "ol" and "steps" in el.classes:
        idx = 1
        for ch in el.children:
            if isinstance(ch, El) and ch.tag == "li":
                badge = El("span", [
                    ("style", "display:inline-flex;align-items:center;justify-content:center;min-width:26px;height:26px;border-radius:50%;background:#2563eb;color:#ffffff;font-weight:700;font-size:13px;margin-right:10px;vertical-align:middle")
                ], ch)
                badge.children.append(Text(str(idx), badge))
                ch.children.insert(0, badge)
                idx += 1

    for ch in el.children:
        if isinstance(ch, El):
            clean_for_wp(ch, lang)


def serialize_text(node):
    if isinstance(node, Text):
        return node.data
    return "".join(serialize_text(c) for c in node.children)


def apply_styles(el, rules, lang):
    if el.tag in ("header", "main", "footer"):
        style = {}
        matched = []
        for idx, (sel, body) in enumerate(rules):
            if match_sel(el, sel):
                matched.append((spec(sel), idx, body))
        matched.sort(key=lambda x: (x[0], x[1]))
        for _, _, body in matched:
            style.update(parse_decls(body))
        _apply_recursive(el, rules, lang, style, inherited_root=True)
    else:
        for ch in el.children:
            if isinstance(ch, El):
                apply_styles(ch, rules, lang)


def _apply_recursive(el, rules, lang, initial_style=None, inherited_root=False):
    style = dict(initial_style or {})
    if not inherited_root:
        matched = []
        for idx, (sel, body) in enumerate(rules):
            if match_sel(el, sel):
                matched.append((spec(sel), idx, body))
        matched.sort(key=lambda x: (x[0], x[1]))
        for _, _, body in matched:
            style.update(parse_decls(body))

    if el.attrs.get("style"):
        style.update(parse_decls(el.attrs["style"]))

    # WordPress-safe overrides
    style["box-sizing"] = "border-box"
    if el.tag == "header":
        style["position"] = "relative"
        style["flex-wrap"] = "wrap"
        style["justify-content"] = "space-between"
        style["gap"] = "10px 14px"
        style.pop("backdrop-filter", None)
        style.pop("-webkit-backdrop-filter", None)
        style["background"] = "#ffffff"
    if el.tag == "ol" and el.parent and "steps" in el.classes:
        style["padding-left"] = "0"
        style["list-style"] = "none"
    if el.parent and el.parent.tag == "ol" and "steps" in el.parent.classes and el.tag == "li":
        style["padding-left"] = "0"
    if "grid" in el.classes:
        if "two" in el.classes:
            style["grid-template-columns"] = "repeat(auto-fill, minmax(min(400px, 100%), 1fr))"
        else:
            style["grid-template-columns"] = "repeat(auto-fill, minmax(min(240px, 100%), 1fr))"
    if "stats" in el.classes:
        style["grid-template-columns"] = "repeat(auto-fit, minmax(min(200px, 100%), 1fr))"
        style["margin-top"] = "16px"
    if "big-download" in el.classes:
        style["margin"] = "18px 0 26px"
    if "font-family" not in style and el.tag in ("p", "li", "h1", "h2", "h3", "a", "td", "th", "summary", "details", "span"):
        if el.tag != "code":
            style["font-family"] = FONT
    if style.get("line-height") is None and el.tag in ("p", "li", "td", "th", "details"):
        style["line-height"] = "1.65"

    # Rewrite attributes
    if "src" in el.attrs:
        src = el.attrs["src"]
        if src.startswith("../assets/"):
            el.attrs["src"] = ASSET_BASE + src[len("../assets/"):]
        elif src.startswith("assets/"):
            el.attrs["src"] = ASSET_BASE + src[len("assets/"):]

    if "href" in el.attrs:
        el.attrs["href"] = rewrite_href(el.attrs["href"], lang)

    if el.tag == "a" and "color" not in style:
        style["color"] = "#2563eb"
        style.setdefault("text-decoration", "none")

    if style:
        el.attrs["style"] = dict_to_style(style)
    for k in ("class", "aria-current", "data-latest-version"):
        el.attrs.pop(k, None)

    for ch in el.children:
        if isinstance(ch, El):
            _apply_recursive(ch, rules, lang)


def esc_attr(v):
    return v.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def serialize(el):
    if isinstance(el, Text):
        return el.data
    if el.tag == "root":
        return "".join(serialize(c) for c in el.children)
    attrs = "".join(f' {k}="{esc_attr(v)}"' for k, v in el.attrs.items())
    if el.tag in VOID:
        return f"<{el.tag}{attrs}>"
    return f"<{el.tag}{attrs}>" + "".join(serialize(c) for c in el.children) + f"</{el.tag}>"


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(SITE, "assets", "office.css"), encoding="utf-8") as f:
        rules = parse_css(f.read())

    for rel, lang, page_key, out_name in PAGES:
        src_path = os.path.join(SITE, rel.replace("/", os.sep))
        with open(src_path, encoding="utf-8") as f:
            html_in = f.read()

        tb = TreeBuilder()
        tb.feed(html_in)
        tb.close()

        # Find body
        body_el = None
        def find_body(n):
            nonlocal body_el
            if isinstance(n, El) and n.tag == "body":
                body_el = n
                return
            for c in getattr(n, "children", []):
                if isinstance(c, El):
                    find_body(c)
        find_body(tb.root)
        assert body_el is not None, f"No body in {rel}"

        clean_for_wp(body_el, lang)
        apply_styles(body_el, rules, lang)

        inner_parts = []
        for ch in body_el.children:
            if isinstance(ch, El) and ch.tag in ("header", "main", "footer"):
                inner_parts.append(serialize(ch))

        wrapper = (
            f'<!-- wp:html -->\n'
            f'<div style="box-sizing:border-box;margin:0;padding:0;background:#f5f7fb;color:#0f172a;font-family:{FONT};line-height:1.65;font-size:16px">\n'
            + "\n".join(inner_parts)
            + "\n</div>\n<!-- /wp:html -->\n"
        )

        out_path = os.path.join(OUT, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(wrapper)
        print(f"Wrote {out_name} ({len(wrapper):,} bytes) -> {WP[lang][page_key]}")


if __name__ == "__main__":
    main()
