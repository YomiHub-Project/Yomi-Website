"""Convert Yomi-Project hub pages (projects/index.html & links/index.html) into
inline-styled WordPress Custom HTML blocks (`<!-- wp:html --> ... <!-- /wp:html -->`).

Usage:
    python3 tools/wp_inline_yp.py [SITE_DIR] [OUT_DIR]
    python3 tools/wp_inline_yp.py . wp-export/yomi-project

Zero third-party dependencies (Python 3 standard library only).
Reads assets/site.css + assets/yomi-project.css, strips <script>/<style>/<svg>/<button>,
filters to a single language via data-lang="vi|en", rewrites the language switcher and
internal links to WordPress paths, converts relative image URLs to absolute GitHub Pages
URLs, and inlines all computed CSS rules into style="..." attributes.
"""

import os
import posixpath
import re
import sys
from html.parser import HTMLParser

BASE = "https://yomihub-project.github.io/Yomi-Website/"

WP_PATHS = {
    "vi": {
        "projects": "/yomi-project/",
        "links": "/yomi-project/lien-ket/",
    },
    "en": {
        "projects": "/yomi-project-en/",
        "links": "/yomi-project-en/links/",
    },
}

YOMIHUB_WP_PATHS = {
    "index.html": "/",
    "en/index.html": "/en/",
}

TARGETS = [
    ("projects/index.html", "projects", "vi", "projects-vi.html"),
    ("projects/index.html", "projects", "en", "projects-en.html"),
    ("links/index.html", "links", "vi", "links-vi.html"),
    ("links/index.html", "links", "en", "links-en.html"),
]

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

STRIP_TAGS = {"script", "style", "svg", "noscript", "template", "input"}

SKIP_PROPS = {
    "transition",
    "animation",
    "view-transition-name",
    "-webkit-font-smoothing",
    "cursor",
    "backdrop-filter",
    "-webkit-backdrop-filter",
    "scroll-behavior",
    "will-change",
    "scroll-margin-top",
    "appearance",
}

# Lowest-priority UA defaults so WordPress theme stylesheets cannot override layout/type
UA_DEFAULTS = {
    "h1": "font-size:2em;margin:0.67em 0;font-weight:bold",
    "h2": "font-size:1.5em;margin:0.83em 0;font-weight:bold",
    "h3": "font-size:1.17em;margin:1em 0;font-weight:bold",
    "h4": "font-size:1em;margin:1.33em 0;font-weight:bold",
    "p": "margin:1em 0",
    "ul": "margin:1em 0;padding-left:40px",
    "ol": "margin:1em 0;padding-left:40px",
    "li": "margin:0",
    "dl": "margin:0",
    "dt": "margin:0",
    "dd": "margin:0",
    "strong": "font-weight:bold",
    "b": "font-weight:bold",
    "em": "font-style:italic",
    "small": "font-size:smaller",
    "code": "font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:0.9em",
    "hr": "margin:0.5em 0",
    "img": "max-width:100%",
    "a": "text-decoration:none",
}

INH_TAGS = {
    "h1", "h2", "h3", "h4", "h5", "h6", "a", "p", "li", "ul", "ol",
    "dl", "dt", "dd", "code", "small", "strong", "b", "em", "span",
    "summary", "details", "blockquote", "table", "th", "td", "hr",
}

INHERIT_PROPS = [
    "color",
    "font-family",
    "line-height",
    "font-weight",
    "letter-spacing",
    "text-align",
    "font-style",
]

CONVERT_TO_DIV = {"header", "main", "footer", "nav", "aside", "section", "article"}


class El:
    __slots__ = ("tag", "attrs", "parent", "children")

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
    __slots__ = ("data", "parent")

    def __init__(self, data, parent=None):
        self.data = data
        self.parent = parent


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = El("root")
        self.cur = self.root
        self.skip_stack = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if self.skip_stack:
            if tag == self.skip_stack[-1] and tag not in VOID_TAGS:
                self.skip_stack.append(tag)
            return
        if tag in STRIP_TAGS:
            if tag not in VOID_TAGS:
                self.skip_stack.append(tag)
            return
        el = El(tag, attrs, self.cur)
        self.cur.children.append(el)
        if tag not in VOID_TAGS:
            self.cur = el

    def handle_startendtag(self, tag, attrs):
        tag = tag.lower()
        if self.skip_stack or tag in STRIP_TAGS:
            return
        el = El(tag, attrs, self.cur)
        self.cur.children.append(el)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.skip_stack:
            if tag == self.skip_stack[-1]:
                self.skip_stack.pop()
            return
        if tag in VOID_TAGS:
            return
        p = self.cur
        while p is not None and p.tag != tag:
            p = p.parent
        if p is not None and p.parent is not None:
            self.cur = p.parent

    def handle_data(self, data):
        if not self.skip_stack:
            self.cur.children.append(Text(data, self.cur))

    def handle_entityref(self, name):
        if not self.skip_stack:
            self.cur.children.append(Text(f"&{name};", self.cur))

    def handle_charref(self, name):
        if not self.skip_stack:
            self.cur.children.append(Text(f"&#{name};", self.cur))


def iter_elements(node):
    if isinstance(node, El):
        yield node
        for ch in node.children:
            if isinstance(ch, El):
                yield from iter_elements(ch)


def css_blocks(css_text):
    css_text = re.sub(r"/\*.*?\*/", "", css_text, flags=re.S)
    out = []
    i = 0
    n = len(css_text)
    while i < n:
        j = css_text.find("{", i)
        if j < 0:
            break
        sel = css_text[i:j].strip()
        depth = 1
        k = j + 1
        while depth and k < n:
            ch = css_text[k]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            k += 1
        out.append((sel, css_text[j + 1 : k - 1]))
        i = k
    return out


def parse_decls(body):
    parts, cur, d = [], [], 0
    for ch in body:
        if ch == "(":
            d += 1
        elif ch == ")":
            d = max(0, d - 1)
        if ch == ";" and d == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    res = []
    for p in parts:
        if ":" in p:
            k, v = p.split(":", 1)
            k = k.strip().lower()
            v = v.strip()
            if k and v:
                res.append((k, v))
    return res


def parse_stylesheets(css_paths):
    rules = []
    root_vars = {}
    for path in css_paths:
        text = open(path, encoding="utf-8").read()
        for sel, body in css_blocks(text):
            if not sel or sel.startswith("@"):
                continue
            ds = parse_decls(body)
            for s in sel.split(","):
                s = s.strip()
                if not s:
                    continue
                if s == ":root":
                    root_vars.update(dict(ds))
                    continue
                if re.search(
                    r"::?(hover|focus|active|visited|before|after|focus-visible|"
                    r"placeholder|marker|selection|target|focus-within|-webkit|view-transition)",
                    s,
                ):
                    continue
                if s.startswith(("html:", "html[")):
                    continue
                rules.append((s, ds))
    return rules, root_vars


def resolve_vars(val, root_vars, depth=0):
    if depth >= 6 or "var(" not in val:
        return val

    def rep(m):
        name = m.group(1).strip()
        fb = (m.group(2) or "").strip()
        raw = root_vars.get(name, fb)
        return resolve_vars(raw, root_vars, depth + 1)

    return re.sub(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)", rep, val)


def selector_specificity(sel):
    s_no_pseudo_fn = re.sub(r"::[\w-]+(\([^)]*\))?", " ", sel)
    ids = len(re.findall(r"#[\w-]+", s_no_pseudo_fn))
    cls = len(re.findall(r"\.[\w-]+|\[[^\]]+\]", s_no_pseudo_fn)) + len(
        re.findall(r"(?<!:):(?!:)[\w-]+", s_no_pseudo_fn)
    )
    stripped = re.sub(r"\[[^\]]+\]|#[\w-]+|\.[\w-]+|:[\w-]+(\([^)]*\))?", " ", s_no_pseudo_fn)
    types = len(re.findall(r"(?:^|[\s>+~])([a-z][a-z0-9]*)", stripped))
    return (ids, cls, types)


def match_atom(el, atom):
    atom = atom.strip()
    if not atom:
        return False
    if atom == "*":
        return True
    m = re.match(r"^([a-zA-Z0-9_-]*)(.*)$", atom)
    tag_req, rest = m.group(1), m.group(2)
    if tag_req and el.tag != tag_req.lower():
        return False

    # Attribute selectors: [attr], [attr="val"]
    for am in re.finditer(r"\[([a-zA-Z0-9_-]+)(?:=[\"']?([^\"'\]]+)[\"']?)?\]", rest):
        attr_name, attr_val = am.group(1), am.group(2)
        if attr_name not in el.attrs:
            return False
        if attr_val is not None and el.attrs.get(attr_name) != attr_val:
            return False
    rest = re.sub(r"\[[^\]]+\]", "", rest)

    # Pseudo-classes (supported structural ones)
    for pseudo in re.findall(r":([a-zA-Z0-9_-]+)", rest):
        if pseudo == "last-child":
            if el.parent is None:
                return False
            sibs = [c for c in el.parent.children if isinstance(c, El)]
            if not sibs or sibs[-1] is not el:
                return False
        elif pseudo == "first-child":
            if el.parent is None:
                return False
            sibs = [c for c in el.parent.children if isinstance(c, El)]
            if not sibs or sibs[0] is not el:
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


def match_selector(el, sel):
    sel = sel.strip()
    if not sel:
        return False
    # Split on direct child combinator '>'
    if ">" in sel:
        parts = [p.strip() for p in sel.split(">")]
        if not match_selector(el, parts[-1]):
            return False
        cur = el
        for p in reversed(parts[:-1]):
            cur = cur.parent
            if cur is None or cur.tag == "root" or not match_selector(cur, p):
                return False
        return True
    if "+" in sel or "~" in sel:
        return False
    atoms = sel.split()
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


def transform_dom(body, page_key, lang):
    other = "en" if lang == "vi" else "vi"

    def walk_clean(node):
        new_children = []
        for ch in node.children:
            if not isinstance(ch, El):
                new_children.append(ch)
                continue

            # 1. Strip nodes belonging exclusively to the other language
            if ch.attrs.get("data-lang") == other:
                continue

            # 2. Convert .lang-switch <button class="lang-opt" data-switch-lang="..."> to styled <a>
            if ch.tag == "button" and "lang-opt" in ch.classes and ch.attrs.get("data-switch-lang"):
                target_lang = ch.attrs["data-switch-lang"]
                a_classes = ["lang-opt"]
                if target_lang == lang:
                    a_classes.append("active")
                a_el = El(
                    "a",
                    [
                        ("class", " ".join(a_classes)),
                        ("href", WP_PATHS[target_lang][page_key]),
                    ],
                    node,
                )
                for sub in ch.children:
                    sub.parent = a_el
                    a_el.children.append(sub)
                new_children.append(a_el)
                continue

            # 3. Strip any other <button> elements (WordPress.com basic strips them)
            if ch.tag == "button":
                continue

            # Recurse into children first
            walk_clean(ch)

            # 4. Unwrap plain <span data-lang="vi|en"> wrappers (no class/id/style)
            if (
                ch.tag == "span"
                and ch.attrs.get("data-lang") == lang
                and not ch.classes
                and not ch.id
                and not ch.attrs.get("style")
            ):
                for sub in ch.children:
                    sub.parent = node
                    new_children.append(sub)
                continue

            # 5. Apply language-specific href override if present
            lang_href = ch.attrs.get(f"data-href-{lang}")
            if lang_href:
                ch.attrs["href"] = lang_href

            new_children.append(ch)
        node.children = new_children

    walk_clean(body)


def rewrite_url(url, page_rel, lang, is_img=False):
    if not url or re.match(r"^(https?:|mailto:|#|data:|/)", url):
        return url
    path_part, _, frag = url.partition("#")
    path_no_q = path_part.split("?")[0]
    base_dir = posixpath.dirname(page_rel)
    if path_no_q in ("", "./"):
        full = posixpath.normpath(base_dir)
    else:
        full = posixpath.normpath(posixpath.join(base_dir, path_no_q))
    full = full.lstrip("./")

    if is_img:
        return BASE + full

    frag_sfx = f"#{frag}" if frag else ""
    if full in ("projects", "projects/index.html"):
        return WP_PATHS[lang]["projects"] + frag_sfx
    if full in ("links", "links/index.html"):
        return WP_PATHS[lang]["links"] + frag_sfx
    if full in YOMIHUB_WP_PATHS:
        return YOMIHUB_WP_PATHS[full] + frag_sfx
    return BASE + full + frag_sfx


def compute_and_inline_styles(body, rules, root_vars, page_rel, lang):
    all_els = list(iter_elements(body))
    computed = {}
    order = 0

    for sel, ds in rules:
        if sel in ("html", "body"):
            targets = [body]
        else:
            targets = [el for el in all_els if match_selector(el, sel)]
        if not targets:
            continue
        sp = selector_specificity(sel)
        for el in targets:
            cur = computed.setdefault(id(el), {})
            for k, v in ds:
                if k.startswith("--") or k in SKIP_PROPS:
                    continue
                imp = "!important" in v
                clean_v = resolve_vars(v.replace("!important", "").strip(), root_vars)
                if not clean_v:
                    continue
                key = (1 if imp else 0, sp, order)
                order += 1
                if k not in cur or cur[k][0] <= key:
                    cur[k] = (key, clean_v)

    def walk_apply(el, inh):
        own = computed.get(id(el), {})
        props = {}

        ua = UA_DEFAULTS.get(el.tag)
        if ua:
            for k, v in parse_decls(ua):
                props[k] = v

        if el.tag in INH_TAGS:
            for k in INHERIT_PROPS:
                if k in inh and k not in own:
                    props[k] = inh[k]

        # Apply matched CSS rules in exact cascade order (important, specificity, source order)
        for k, (_key, v) in sorted(own.items(), key=lambda item: item[1][0]):
            if v == "inherit" and k in inh:
                props[k] = inh[k]
            else:
                props[k] = v

        # Preserve any explicit inline style from source HTML
        if el.attrs.get("style"):
            for k, v in parse_decls(el.attrs["style"]):
                props[k] = resolve_vars(v, root_vars)

        # Ensure CSS grid minmax(Npx, ...) never overflows narrow viewports
        if "grid-template-columns" in props:
            props["grid-template-columns"] = re.sub(
                r"minmax\((\d+px),",
                r"minmax(min(\1, 100%),",
                props["grid-template-columns"],
            )

        if el.tag == "li" and inh.get("_ls") == "none" and "list-style" not in props:
            props["list-style"] = "none"

        new_inh = dict(inh)
        if el.tag in ("ul", "ol"):
            new_inh["_ls"] = props.get("list-style", props.get("list-style-type", ""))
        for k in INHERIT_PROPS:
            if k in props:
                new_inh[k] = props[k]

        if props:
            el.attrs["style"] = ";".join(f"{k}:{v}" for k, v in props.items())

        if "src" in el.attrs:
            el.attrs["src"] = rewrite_url(el.attrs["src"], page_rel, lang, is_img=True)
        if "href" in el.attrs:
            el.attrs["href"] = rewrite_url(el.attrs["href"], page_rel, lang, is_img=False)
        el.attrs.pop("srcset", None)

        for ch in el.children:
            if isinstance(ch, El):
                walk_apply(ch, new_inh)

    walk_apply(body, {})


def finalize_wp_dom(body):
    for el in iter_elements(body):
        if el.tag in CONVERT_TO_DIV:
            el.tag = "div"
        el.attrs.pop("class", None)
        for attr in list(el.attrs):
            if attr.startswith("data-") or attr in (
                "aria-current",
                "aria-pressed",
                "aria-label",
                "aria-hidden",
                "role",
                "tabindex",
                "hreflang",
                "lang",
                "loading",
                "decoding",
            ):
                el.attrs.pop(attr, None)

    body.tag = "div"
    st = body.attrs.get("style", "")
    extra = "margin:0;min-height:100vh;width:100%"
    body.attrs["style"] = f"{st};{extra}" if st else extra


def esc_attr(val):
    return (
        val.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def serialize(node):
    if isinstance(node, Text):
        return node.data
    attrs = "".join(f' {k}="{esc_attr(v)}"' for k, v in node.attrs.items())
    if node.tag in VOID_TAGS:
        return f"<{node.tag}{attrs}>"
    inner = "".join(serialize(c) for c in node.children)
    return f"<{node.tag}{attrs}>{inner}</{node.tag}>"


def find_body(root):
    for el in iter_elements(root):
        if el.tag == "body":
            return el
    return None


def convert_page(site_dir, page_rel, page_key, lang, rules, root_vars):
    html_src = open(os.path.join(site_dir, page_rel.replace("/", os.sep)), encoding="utf-8").read()
    tb = TreeBuilder()
    tb.feed(html_src)
    tb.close()

    body = find_body(tb.root)
    if body is None:
        raise RuntimeError(f"No <body> found in {page_rel}")

    transform_dom(body, page_key, lang)
    compute_and_inline_styles(body, rules, root_vars, page_rel, lang)
    finalize_wp_dom(body)

    html_out = serialize(body)
    html_out = re.sub(r"\n\s*\n+", "\n", html_out)
    return "<!-- wp:html -->\n" + html_out + "\n<!-- /wp:html -->\n"


def main():
    site_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(site_dir, "wp-export", "yomi-project")

    css_paths = [
        os.path.join(site_dir, "assets", "site.css"),
        os.path.join(site_dir, "assets", "yomi-project.css"),
    ]
    rules, root_vars = parse_stylesheets(css_paths)
    os.makedirs(out_dir, exist_ok=True)

    for page_rel, page_key, lang, out_name in TARGETS:
        out_html = convert_page(site_dir, page_rel, page_key, lang, rules, root_vars)
        out_path = os.path.join(out_dir, out_name)
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(out_html)
        print(f"{out_name} -> {WP_PATHS[lang][page_key]} ({len(out_html):,} bytes)")


if __name__ == "__main__":
    main()
