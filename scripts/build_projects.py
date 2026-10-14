"""Build public project pages without external dependencies. Run from any directory."""
from html import escape as esc
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from research_visuals import (validate_insight, diagram_markup, evidence_markup,
                              research_brief, takeaways_markup)

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nousphera.github.io'
ICONS = {
    'arrow': '<path d="M7 17 17 7M7 7h10v10"/>',
    'paper': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h6"/>',
    'code': '<path d="m8 7-5 5 5 5m8-10 5 5-5 5m-3-13-2 16"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
    'moon': '<path d="M20.8 13A9 9 0 0 1 11 3.2 9 9 0 1 0 20.8 13Z"/>',
    'auto': '<rect x="3" y="3" width="18" height="14" rx="2"/><path d="M8 21h8m-4-4v4m0-18v14"/>',
    'copy': '<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
    'expand': '<path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>',
    'close': '<path d="m6 6 12 12M6 18 18 6"/>',
    'back': '<path d="m12 5-7 7 7 7M5 12h14"/>',
    'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>'
}

def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

def public_url(value):
    u = urlparse(value)
    if u.scheme != 'https' or not u.netloc or u.hostname in ('localhost', '127.0.0.1'):
        raise ValueError(f'Expected public HTTPS URL: {value}')
    return value

def validate(p):
    required = ('slug', 'library_id', 'name', 'title', 'year', 'venue', 'type', 'authors', 'tagline', 'summary', 'category', 'topics', 'accent', 'accent_dark', 'tint', 'links', 'figure', 'method', 'findings', 'abstract', 'bibtex', 'provenance')
    for key in required:
        if not p.get(key):
            raise ValueError(f'{p.get("slug")}: missing {key}')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', p['slug']):
        raise ValueError('Invalid slug')
    for color in ('accent', 'accent_dark', 'tint'):
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', p[color]):
            raise ValueError('Invalid color')
    for url in p['links'].values():
        public_url(url)
    public_url(p['provenance']['source_url'])
    for r in p.get('related', []):
        public_url(r['url'])
    if p.get('abstract_source'):
        public_url(p['abstract_source']['url'])
    for key in ('figure', 'secondary_figure'):
        if key in p:
            f = p[key]
            source = Path(f['src'])
            if source.is_absolute() or '..' in source.parts or not f['src'].startswith(f'assets/projects/{p["slug"]}/'):
                raise ValueError('Figure must be local to project')
            public_url(f['source_url'])
            if not f.get('alt') or not f.get('caption') or not f.get('source_label'):
                raise ValueError('Figure needs accessible text and attribution')
    raw = json.dumps(p)
    if '/Users/' in raw or 'FederatedML' in raw or 'file://' in raw:
        raise ValueError('Internal path or retired organization in public content')

def load_projects():
    projects = [json.loads(p.read_text()) for p in sorted((ROOT / 'data/projects').glob('*.json'))]
    for p in projects:
        validate(p)
        insight_path = ROOT / 'data/insights' / (p['slug'] + '.json')
        if insight_path.exists():
            insight = json.loads(insight_path.read_text())
            validate_insight(insight, public_url)
            if insight['slug'] != p['slug']:
                raise ValueError('Insight does not match paper')
            p['insight'] = insight
    return sorted(projects, key=lambda p: (-p['year'], p['name'].lower()))

def theme_control():
    symbols = ''.join(f'<span data-theme-icon="{m}">{icon(m if m == "auto" else "sun" if m == "light" else "moon")}</span>' for m in ('auto', 'light', 'dark'))
    return f'<button class="theme-toggle" type="button" aria-label="Theme: automatic. Switch to light theme." title="Theme: automatic. Switch to light theme.">{symbols}<span data-theme-label>Auto</span></button>'

def header():
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner"><a class="brand" href="/" aria-label="Nousphera home"><span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>Nousphera</a>
<nav aria-label="Main navigation"><a href="/projects/">Projects</a><a class="wide-nav" href="https://github.com/Nousphera">GitHub {icon('arrow')}</a><a class="wide-nav" href="https://vtsouval.github.io/">Vasileios Tsouvalas {icon('arrow')}</a>{theme_control()}</nav></div></header>'''

def footer():
    return '''<footer class="site-footer"><a class="brand" href="/">Nousphera</a><p>Research in collaborative and efficient machine learning.</p><div><a href="https://github.com/Nousphera">GitHub</a><a href="https://vtsouval.github.io/">Vasileios Tsouvalas</a><a href="mailto:nousphera@proton.me">Email</a></div></footer>'''

def shell(title, description, path, body, p=None):
    meta = ''
    css = ''
    if p:
        citation_year = re.search(r'year\s*=\s*\{(\d{4})\}', p['bibtex']).group(1)
        css = f'<style>:root{{--accent-light:{p["accent"]};--accent-dark:{p["accent_dark"]};--tint-light:{p["tint"]};}}</style>'
        for key, value in [('citation_title', p['title']), ('citation_publication_date', citation_year)] + [('citation_author', a) for a in p['authors']]:
            meta += f'<meta name="{key}" content="{esc(value)}">\n'
        preview = p.get('social_image', p['figure']['src'])
        meta += f'<meta property="og:image" content="{ORIGIN}/{esc(preview)}">\n'
        data = {'@context': 'https://schema.org', '@type': 'ScholarlyArticle', 'headline': p['title'], 'description': p['summary'], 'author': [{'@type': 'Person', 'name': a} for a in p['authors']], 'datePublished': citation_year, 'url': ORIGIN + path, 'sameAs': [url for label, url in p['links'].items() if label not in ('Code', 'Project')], 'image': ORIGIN + '/' + p['figure']['src']}
        meta += '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026') + '</script>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Nousphera</title><meta name="description" content="{esc(description)}">
<meta name="color-scheme" content="light dark"><link rel="canonical" href="{ORIGIN}{path}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{ORIGIN}{path}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<script src="/assets/theme.js"></script><link rel="stylesheet" href="/assets/projects.css"><link rel="stylesheet" href="/assets/research.css">{css}{meta}
<script src="/assets/projects.js" defer></script><script src="/assets/project-tabs.js" defer></script></head><body>{header()}{body}{footer()}</body></html>\n'''

def figure_markup(f, primary=False):
    return f'''<figure class="paper-figure {'primary-figure' if primary else 'result-figure'}"><a class="figure-open" href="/{esc(f['src'])}" data-figure data-caption="{esc(f['caption'])}" aria-label="Enlarge figure: {esc(f['alt'])}"><img src="/{esc(f['src'])}" width="{int(f['width'])}" height="{int(f['height'])}" style="aspect-ratio:{int(f['width'])}/{int(f['height'])}" alt="{esc(f['alt'])}" {'fetchpriority="high"' if primary else 'loading="lazy"'} decoding="async"><span class="expand-label">{icon('expand')}<span>Enlarge</span></span></a><figcaption>{esc(f['caption'])} <a href="{esc(f['source_url'])}">{esc(f['source_label'])} {icon('arrow')}</a></figcaption></figure>'''

def resources(p):
    links = []
    for label, url in p['links'].items():
        if label == 'Project':
            continue
        links.append(f'<a class="resource {"primary" if label == "Paper" else ""}" href="{esc(url)}">{icon("code" if label == "Code" else "paper" if label == "Paper" else "arrow")}{esc(label)}</a>')
    links.append(f'<a class="resource" href="#citation">{icon("copy")}Cite</a>')
    return '<div class="resource-links">' + ''.join(links) + '</div>'

def project_page(p, projects):
    insight = p.get('insight')
    venue = p['venue'] if str(p['year']) in p['venue'] else f'{p["venue"]} · {p["year"]}'
    abstract_source = p.get('abstract_source', {'url': p['provenance']['source_url'], 'label': 'Source abstract'})
    source_note = f'<p class="source-note"><a href="{esc(abstract_source["url"])}">{esc(abstract_source["label"])} {icon("arrow")}</a> {esc(abstract_source.get("note", ""))}</p>'
    authors = ' <span class="author-separator" aria-hidden="true">·</span> '.join(f'<span>{esc(a)}</span>' for a in p['authors'])
    methods = ''.join(f'<li><span class="step-number">{i:02d}</span><div><h3>{esc(s["title"])}</h3><p>{esc(s["text"])}</p></div></li>' for i, s in enumerate(p['method'], 1))
    findings = ''.join(f'<article><h3>{esc(s["title"])}</h3><p>{esc(s["text"])}</p></article>' for s in p['findings'])
    related = ''
    if p.get('related'):
        related = '<div class="related-versions"><h3>Related publication</h3>' + ''.join(f'<a href="{esc(r["url"])}">{esc(r["label"])} {icon("arrow")}</a>' for r in p['related']) + '</div>'
    secondary = figure_markup(p['secondary_figure']) if p.get('secondary_figure') else ''
    visual = figure_markup(p['figure'], True)
    takeaways = ''
    results = f'<section id="findings" data-tab-panel class="section findings-section"><div class="section-heading"><span class="kicker">From the paper</span><h2>Key findings</h2></div><div class="findings">{findings}</div></section>{secondary}'
    originals = ''
    if insight:
        visual = research_brief(insight) + diagram_markup(insight['diagram'], p['slug'])
        visual += f'<p class="diagram-source"><a href="{esc(insight["evidence_inventory"]["source_url"])}">Method overview · Based on the paper {icon("arrow")}</a></p>'
        takeaways = takeaways_markup(insight)
        results = evidence_markup(insight)
        original_primary = '' if 'Explanatory schematic' in p['figure']['source_label'] else figure_markup(p['figure'])
        originals = f'<details class="original-figures"><summary>Original paper figures &amp; sources</summary>{original_primary}{secondary}</details>'
    others = sorted((q for q in projects if q['slug'] != p['slug']), key=lambda q: (-len(set(p['topics']) & set(q['topics'])), q['category'] != p['category'], -q['year']))[:2]
    more = ''.join(f'<a href="/projects/{q["slug"]}/"><span>{esc(q["name"])}</span><p>{esc(q["tagline"])}</p>{icon("arrow")}</a>' for q in others)
    body = f'''<main id="main" class="project-main"><div class="breadcrumb"><a href="/projects/">{icon('back')}All projects</a><span>{esc(p['category'])}</span></div>
<section class="paper-hero" aria-labelledby="paper-title"><div class="eyebrow"><span class="project-name">{esc(p['name'])}</span><span>{esc(venue)}</span></div>
<h1 id="paper-title">{esc(p['title'])}</h1><p class="tagline">{esc(p['tagline'])}</p><p class="authors">{authors}</p>{resources(p)}</section>
<nav class="section-nav" data-project-tabs aria-label="On this page"><a href="#overview">Overview</a><a href="#method">Method</a><a href="#findings">Results</a><a href="#citation">Citation</a></nav>
<div id="overview" data-tab-panel class="overview-panel">{visual}<section class="overview section"><div class="section-heading"><span class="kicker">The idea</span><h2>At a glance</h2></div><div><p class="overview-text">{esc(p['summary'])}</p>{takeaways}<ul class="topics">{''.join(f'<li>{esc(t)}</li>' for t in p['topics'])}</ul><details class="abstract"><summary>Read the abstract</summary><p>{esc(p['abstract'])}</p>{source_note}</details></div></section></div>
<section id="method" data-tab-panel class="section method-section"><div class="section-heading"><span class="kicker">The approach</span><h2>How it works</h2></div><div><ol class="method-steps">{methods}</ol>{originals}</div></section>
{results}
<section id="citation" data-tab-panel class="section citation-section"><div class="section-heading"><span class="kicker">Reference</span><h2>Cite this work</h2></div><div class="citation-content"><div class="citation-bar"><span>BibTeX</span><div><a href="citation.bib" download>Download .bib</a><button type="button" data-copy-citation>{icon('copy')}<span>Copy</span></button></div></div><pre tabindex="0" aria-label="BibTeX citation"><code id="bibtex">{esc(p['bibtex'].strip())}</code></pre><span class="copy-status sr-only" role="status"></span>{related}</div></section>
<section class="more-projects" aria-label="Explore related projects"><h2>Keep exploring</h2><div>{more}</div></section></main>
<dialog class="figure-dialog" aria-label="Enlarged paper figure"><div class="dialog-toolbar"><span>Figure preview</span><button type="button" data-close-figure aria-label="Close figure">{icon('close')}</button></div><div class="dialog-scroll"><img alt=""></div><p class="dialog-caption"></p><a class="dialog-original" href="#" target="_blank" rel="noopener">Open full-size image {icon('arrow')}</a></dialog>'''
    return shell(p['name'] + ' — ' + p['title'], p['summary'], f'/projects/{p["slug"]}/', body, p)

def card(p):
    keywords = ' '.join([p['name'], p['title'], p['tagline'], p['category'], p['venue'], *p['authors'], *p['topics'], *p.get('keywords', [])]).lower()
    visual = diagram_markup(p['insight']['diagram'], p['slug'], compact=True) if p.get('insight') else f'<img src="/{esc(p["figure"]["src"])}" width="{int(p["figure"]["width"])}" height="{int(p["figure"]["height"])}" alt="" loading="lazy" decoding="async">'
    return f'''<article class="project-card" data-category="{esc(p['category'])}" data-search="{esc(keywords)}" style="--card-accent:{p['accent']};--card-tint:{p['tint']};--card-accent-dark:{p['accent_dark']}"><a href="/projects/{p['slug']}/" class="card-link"><div class="card-visual">{visual}</div><div class="card-content"><div class="card-meta"><span>{esc(p['category'])}</span><span>{p['year']}</span></div><h2>{esc(p['name'])}{icon('arrow')}</h2><p>{esc(p['tagline'])}</p><span class="card-venue">{esc(p['venue'])}</span></div></a></article>'''

def gallery_page(projects, home=False):
    categories = list(dict.fromkeys(p['category'] for p in projects))
    buttons = ''.join(f'<button type="button" data-filter="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in categories)
    title = 'Learning together.<br><span>With less.</span>' if home else 'Research projects<span>.</span>'
    intro = 'Methods for efficient, reliable and private learning across devices, tasks and data.' if home else 'The ideas, methods and results behind our papers.'
    body = f'''<main id="main" class="gallery-main"><section class="gallery-hero"><p class="eyebrow">Nousphera · Research &amp; open source</p><h1>{title}</h1><p>{intro}</p><a class="text-link" href="https://github.com/Nousphera">Explore the code {icon('arrow')}</a></section>
<section aria-label="Research project collection"><div class="collection-heading"><h2>Paper projects <span>{len(projects):02d}</span></h2><label class="project-search">{icon('search')}<span class="sr-only">Search projects</span><input type="search" id="project-search" placeholder="Search projects" autocomplete="off"></label></div><div class="filter-bar" aria-label="Filter projects"><button type="button" data-filter="all" aria-pressed="true">All projects</button>{buttons}</div><p class="sr-only" id="filter-status" role="status">{len(projects)} projects</p><div class="project-grid">{''.join(card(p) for p in projects)}</div><p class="no-results" hidden>No matching projects. Try another topic or clear the filters.</p></section></main>'''
    return shell('Research projects' if not home else 'Collaborative machine learning', intro, '/' if home else '/projects/', body)

def build():
    projects = load_projects()
    if len(projects) != 14:
        raise ValueError(f'Expected all 14 paper projects; found {len(projects)}')
    for p in projects:
        folder = ROOT / 'projects' / p['slug']
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'index.html').write_text(project_page(p, projects))
        (folder / 'citation.bib').write_text(p['bibtex'].strip() + '\n')
    (ROOT / 'projects/index.html').write_text(gallery_page(projects))
    (ROOT / 'index.html').write_text(gallery_page(projects, home=True))
    # Keep the former landing-page data endpoint useful for existing consumers.
    compatibility = [{'id': p['slug'], 'title': p['title'], 'focus': p['category'], 'year': p['year'], 'venue': p['venue'], 'description': p['summary'], 'link': {'href': f'{ORIGIN}/projects/{p["slug"]}/', 'label': 'Project page'}} for p in projects]
    (ROOT / 'assets/publications.json').write_text(json.dumps(compatibility, indent=2, ensure_ascii=False) + '\n')
    urls = ['/', '/projects/'] + [f'/projects/{p["slug"]}/' for p in projects]
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{ORIGIN}{path}</loc></url>\n' for path in urls) + '</urlset>\n')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n')
    (ROOT / '.nojekyll').touch()
    print(f'Built {len(projects)} paper pages, project gallery, home page and sitemap.')

if __name__ == '__main__':
    build()
