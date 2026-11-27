import re, sys, os, json
from bs4 import BeautifulSoup, Comment
import soupsieve as sv

# 27/11/2026: bản cho website Tử Vi (applied-astrology/) – dựa trên tools/wp_inline.py.
# Dùng: python3 tools/wp_inline_aa.py . wp-export/applied-astrology
# Mỗi trang song ngữ được tách thành 2 trang WordPress (vi + en) vì WordPress không chạy JS đổi ngôn ngữ.
SITE = sys.argv[1]; OUT = sys.argv[2]
BASE = 'https://yomihub-project.github.io/Yomi-Website/'
css = open(os.path.join(SITE, 'applied-astrology/assets/aa.css'), encoding='utf-8').read()
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)

def blocks(s):
    i, out = 0, []
    while i < len(s):
        j = s.find('{', i)
        if j < 0: break
        sel = s[i:j].strip(); depth = 1; k = j + 1
        while depth and k < len(s):
            if s[k] == '{': depth += 1
            elif s[k] == '}': depth -= 1
            k += 1
        out.append((sel, s[j+1:k-1])); i = k
    return out

def decls(body):
    parts, cur, d = [], '', 0
    for ch in body:
        if ch == '(': d += 1
        if ch == ')': d -= 1
        if ch == ';' and d == 0: parts.append(cur); cur = ''
        else: cur += ch
    parts.append(cur)
    res = []
    for p in parts:
        if ':' in p:
            k, v = p.split(':', 1); k = k.strip().lower(); v = v.strip()
            if k and v: res.append((k, v))
    return res

rules = []; root = {}
for sel, body in blocks(css):
    if sel.startswith('@'): continue   # font-face, media, keyframes, view-transition
    for s in sel.split(','):
        s = s.strip()
        if s == ':root':
            root.update(dict(decls(body))); continue
        rules.append((s, decls(body)))

def resolve(v, depth=0):
    def rep(m):
        name, fb = m.group(1).strip(), (m.group(2) or '').strip()
        return resolve(root.get(name, fb), depth+1) if depth < 5 else fb
    return re.sub(r'var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)', rep, v)

SKIP = {'transition','animation','view-transition-name','-webkit-font-smoothing','cursor','backdrop-filter','scroll-behavior','will-change','scroll-margin-top','-webkit-backdrop-filter'}
def spec(s):
    s2 = re.sub(r'::?[\w-]+(\([^)]*\))?', lambda m: ' PSEUDO ', s)
    ids = s.count('#'); cls = len(re.findall(r'\.[\w-]+|\[[^\]]+\]', s)) + len(re.findall(r'(?<!:):(?!:)[\w-]+', s))
    types = len(re.findall(r'(?:^|[\s>+~])([a-z][a-z0-9]*)', s2.replace('PSEUDO','')))
    return (ids, cls, types)

# UA defaults (lowest priority) so theme rules don't take over
UA = {'h1':'font-size:2em;margin:0.67em 0;font-weight:bold','h2':'font-size:1.5em;margin:0.83em 0;font-weight:bold',
      'h3':'font-size:1.17em;margin:1em 0;font-weight:bold','h4':'font-size:1em;margin:1.33em 0;font-weight:bold',
      'p':'margin:1em 0','ul':'margin:1em 0;padding-left:40px','ol':'margin:1em 0;padding-left:40px',
      'strong':'font-weight:bold','b':'font-weight:bold','em':'font-style:italic','small':'font-size:smaller',
      'code':"font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:0.9em",'hr':'margin:0.5em 0',
      'li':'margin:0','img':'max-width:100%','a':'text-decoration:none'}
INH_TAGS = {'h1','h2','h3','h4','h5','h6','a','p','li','ul','ol','code','small','strong','em','summary','details','blockquote','span','button','table','th','td','hr'}
INHERIT = ['color','font-family','line-height','font-weight','letter-spacing','text-align','font-style']

EXTRA = {
 'hero-index':'display:flex;flex-wrap:wrap;align-items:center;gap:32px',
 'hero-text':'flex:1 1 420px;min-width:0',
 'hero-visual':'flex:1 1 300px;min-width:0',
 'guide-layout':'display:flex;flex-wrap:wrap;align-items:flex-start;gap:32px',
 'guide-sidebar':'flex:0 1 280px;min-width:0',
 'guide-main':'flex:1 1 480px;min-width:0',
 'hero-compact':'flex-wrap:wrap',
 'top-bar':'flex-wrap:wrap',
 'bookmark-nav':'flex-wrap:wrap',
 'dl-item':'display:flex;flex-wrap:wrap;align-items:center;gap:12px 16px',
 'lang-toggle':'text-decoration:none;display:inline-block',
 'dl-btn':'font-size:22px;font-weight:800;line-height:1',
 'site-nav':'display:flex;flex-wrap:wrap',
 'cosmic-wrap':'',
}
# đường dẫn trang WordPress (slug con của trang cha) – sửa ở đây nếu đặt slug khác
WP = {'vi': {'applied-astrology/index.html':'/tu-vi-ung-dung/','applied-astrology/download.html':'/tu-vi-ung-dung/tai-xuong/',
             'applied-astrology/guide.html':'/tu-vi-ung-dung/huong-dan/','applied-astrology/privacy.html':'/tu-vi-ung-dung/chinh-sach-quyen-rieng-tu/'},
      'en': {'applied-astrology/index.html':'/applied-astrology/','applied-astrology/download.html':'/applied-astrology/download/',
             'applied-astrology/guide.html':'/applied-astrology/guide/','applied-astrology/privacy.html':'/applied-astrology/privacy/'}}
LANG = 'vi'
PAGES = WP['vi']

def fix_url(u, page):
    if not u or re.match(r'^(https?:|mailto:|#|data:|/)', u): return u
    d = os.path.dirname(page)
    path, _, frag = u.partition('#'); path = path.split('?')[0]
    full = os.path.normpath(os.path.join(d, path)).replace('\\','/') if path else page
    if full in PAGES: return PAGES[full] + (('#'+frag) if frag else '')
    YH = {'index.html': '/', 'en/index.html': '/en/'}   # trang YomiHub trên cùng site WordPress (theo tools/wp_inline.py)
    if full in YH: return YH[full] + (('#'+frag) if frag else '')
    return BASE + full + (('#'+frag) if frag else '')

def convert(page):
    soup = BeautifulSoup(open(os.path.join(SITE, page), encoding='utf-8').read(), 'html.parser')
    body = soup.body
    other = 'en' if LANG == 'vi' else 'vi'
    for t in body.select('.%s-only' % other): t.decompose()
    for t in body.select('.cosmic-bg, .to-top, .nav-toggle'): t.decompose()
    # nút đổi ngôn ngữ (JS) -> liên kết sang trang ngôn ngữ kia
    btn = body.select_one('button.lang-toggle')
    if btn:
        a2 = soup.new_tag('a', href=WP[other][page], attrs={'class': 'lang-toggle'})
        a2.string = 'English' if LANG == 'vi' else 'Tiếng Việt'
        btn.replace_with(a2)
    for el in body.select('.vi-only, .en-only'): el.unwrap()
    for sv_ in body.select('.dl-btn svg'):
        sv_.replace_with('⬇')
    for sv_ in body.select('.logo-badge svg'):
        sv_.replace_with(soup.new_tag('img', src=BASE + 'applied-astrology/assets/logo-68.png', alt='Yomi', width='34', height='34', style='display:block;width:34px;height:34px;border-radius:8px'))
    for t in body.find_all(['script','svg','button','input','noscript','template']): t.decompose()
    for c in body.find_all(string=lambda x: isinstance(x, Comment)): c.extract()
    for t in body.select('.guide-search-box, .dl-hash-box, .eng-banner, .lang-banner'): t.decompose()
    for t in body.select('.dl-size'):
        if 'Chờ' in t.get_text() or 'Pending' in t.get_text() or 'pending' in t.get_text(): t.decompose()
    for ul in body.select('ul.toc-list, #toc-list'):
        if not ul.find('li'):
            main = body.select_one('.guide-main')
            for h in (main.find_all('h2') if main else []):
                sec = h if h.get('id') else h.find_parent(id=True)
                if not sec or not sec.get('id'): continue
                li = soup.new_tag('li', attrs={'class':'toc-item'}); a = soup.new_tag('a', href='#'+sec['id'], attrs={'class':'toc-link'})
                a.string = h.get_text(' ', strip=True); li.append(a); ul.append(li)
    for li in body.find_all('li'):
        if 'kiritokmn' in li.get_text().lower(): li.decompose()
    computed = {}
    order = 0
    for s, ds in rules:
        if re.search(r'::?(hover|focus|active|visited|before|after|focus-visible|placeholder|marker|selection|target|focus-within|-webkit)', s): continue
        if s in ('html','body'):
            targets = [body]
        else:
            try: targets = sv.select(s, body)
            except Exception: continue
        sp = spec(s)
        for el in targets:
            for k, v in ds:
                if k.startswith('--') or k in SKIP: continue
                imp = '!important' in v; v = resolve(v.replace('!important','').strip())
                key = (1 if imp else 0, sp, order); order += 1
                cur = computed.setdefault(id(el), {})
                if k not in cur or cur[k][0] <= key: cur[k] = (key, v)
    def walk(el, inh):
        own = computed.get(id(el), {})
        props = {}
        ua = UA.get(el.name)
        if ua:
            for k, v in decls(ua): props[k] = v
        if el.name in INH_TAGS:
            for k in INHERIT:
                if k in inh and k not in own: props[k] = inh[k]
        if 'font-size' in inh and not re.search(r'(em|%)$', inh['font-size']) and 'font-size' not in own and el.name not in ('h1','h2','h3','h4','small','code'):
            pass
        for k, (key, v) in sorted(own.items(), key=lambda x: x[1][0]): props[k] = v
        if el.get('style'):
            for k, v in decls(el['style']): props[k] = v
        for c in (el.get('class') or []):
            for k, v in decls(EXTRA.get(c, '')): props[k] = v
        if 'grid-template-columns' in props:
            props['grid-template-columns'] = re.sub(r'minmax\((\d+px),', r'minmax(min(\1, 100%),', props['grid-template-columns'])
        if el.name == 'li' and inh.get('_ls') == 'none' and 'list-style' not in props: props['list-style'] = 'none'
        newinh = dict(inh)
        newinh['_ls'] = props.get('list-style', props.get('list-style-type', '')) if el.name in ('ul','ol') else inh.get('_ls')
        for k in INHERIT:
            if k in props: newinh[k] = props[k]
        if props: el['style'] = ';'.join(f'{k}:{v}' for k, v in props.items())
        for a in ('href','src'):
            if el.get(a): el[a] = fix_url(el[a], page)
        if el.get('srcset'): del el['srcset']
        for c in el.find_all(recursive=False): walk(c, newinh)
    walk(body, {})
    for t in body.find_all(['header','main','footer','nav','aside']): t.name = 'div'
    for el in body.find_all(True):
        if el.get('class'): del el['class']
        for a in list(el.attrs):
            if a.startswith('data-') or a in ('aria-current','role','tabindex','hreflang','lang','loading','decoding'): del el[a]
    body.name = 'div'
    st = body.get('style','')
    body['style'] = st + ';margin:0;min-height:100vh;width:100%'
    html = str(body)
    html = re.sub(r'\n\s*\n+', '\n', html)
    return '<!-- wp:html -->\n' + html + '\n<!-- /wp:html -->'

os.makedirs(OUT, exist_ok=True)
BG = ('background:radial-gradient(circle at 80% 15%, rgba(100,70,240,0.15) 0%, transparent 45%),'
      'radial-gradient(circle at 10% 75%, rgba(229,181,103,0.12) 0%, transparent 40%),'
      'radial-gradient(circle at 20% 20%, #1a1b35 0%, #0c0d1a 60%, #05060b 100%)')
for LANG in ('vi', 'en'):
    PAGES = WP[LANG]
    for p in PAGES:
        out = convert(p)
        out = out.replace('position:sticky', 'position:relative').replace('position: sticky', 'position:relative')
        out = out.replace('<div style="', '<div style="' + BG + ';', 1)
        # WordPress.com (kses) bỏ background-clip / -webkit-text-fill-color -> chữ gradient thành khối nền: đổi sang chữ màu đặc
        so = BeautifulSoup(out, 'html.parser')
        for el in so.find_all(style=True):
            st = el['style']
            if 'text-fill-color' in st:
                ds = [d for d in st.split(';') if d.split(':')[0].strip() not in ('background', 'background-image', '-webkit-background-clip', 'background-clip', '-webkit-text-fill-color')]
                el['style'] = ';'.join(ds) + ';color:#f5e6c8'
        out = str(so)
        name = LANG + '_' + os.path.basename(p)
        open(os.path.join(OUT, name), 'w', encoding='utf-8').write(out)
        print(name, PAGES[p], len(out))
