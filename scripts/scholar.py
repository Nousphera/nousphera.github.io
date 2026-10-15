"""Static scholarly records and Highwire metadata for the paper collection."""
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nousphera.github.io'


def record(p):
    item = json.loads((ROOT / 'data/scholar' / (p['slug'] + '.json')).read_text())
    pdf = ROOT / 'projects' / p['slug'] / 'paper.pdf'
    raw = pdf.read_bytes()
    if not raw.startswith(b'%PDF-') or len(raw) > 5_000_000:
        raise ValueError(f'{p["slug"]}: expected a searchable PDF below 5 MB')
    if sha256(raw).hexdigest() != item['sha256']:
        raise ValueError(f'{p["slug"]}: paper changed; review its source record')
    return item


def fields(p):
    item = record(p)
    bib = dict(re.findall(r'^\s*(\w+)\s*=\s*\{([^\n]*)\},?\s*$', p['bibtex'], re.M))
    base = f'{ORIGIN}/projects/{p["slug"]}/'
    result = [('citation_title', p['title'])]
    result += [('citation_author', author) for author in p['authors']]
    result += [('citation_publication_date', bib['year']),
               ('citation_language', 'en'),
               ('citation_abstract_html_url', base + 'paper.html'),
               ('citation_pdf_url', base + 'paper.pdf')]
    mapping = {'doi': 'citation_doi', 'journal': 'citation_journal_title',
               'booktitle': 'citation_conference_title', 'volume': 'citation_volume',
               'number': 'citation_issue', 'publisher': 'citation_publisher',
               'articleno': 'citation_article_number'}
    for key, tag in mapping.items():
        if bib.get(key):
            result.append((tag, bib[key].replace('{', '').replace('}', '')))
    if bib.get('pages'):
        pages = re.split(r'--|–', bib['pages'])
        result.append(('citation_firstpage', pages[0]))
        if len(pages) == 2:
            result.append(('citation_lastpage', pages[1]))
    elif bib.get('articleno'):
        result += [('citation_firstpage', '1'), ('citation_lastpage', bib['numpages'])]
    if item.get('arxiv_id'):
        result.append(('citation_arxiv_id', item['arxiv_id']))
    result += list(item.get('metadata', {}).items())
    return result


def metadata(p):
    return ''.join(f'<meta name="{escape(k)}" content="{escape(v, quote=True)}">\n'
                   for k, v in fields(p))


def archive_link(p):
    return (f'<a class="paper-archive-link" href="/projects/{p["slug"]}/paper.html">'
            'Abstract &amp; full text</a>')


def abstract_page(p):
    item = record(p)
    base = f'{ORIGIN}/projects/{p["slug"]}/'
    authors = ' · '.join(f'<strong>{escape(a)}</strong>' if a == 'Vasileios Tsouvalas'
                         else escape(a) for a in p['authors'])
    bib = dict(fields(p))
    venue = bib.get('citation_journal_title') or bib.get('citation_conference_title') or 'arXiv'
    citation = venue + ' · ' + bib['citation_publication_date']
    for k, label in [('citation_volume', 'Vol. '), ('citation_issue', 'No. '),
                     ('citation_article_number', 'Article ')]:
        if bib.get(k):
            citation += ' · ' + label + bib[k]
    if bib.get('citation_firstpage') and not bib.get('citation_article_number'):
        citation += ' · ' + bib['citation_firstpage']
        if bib.get('citation_lastpage'):
            citation += '–' + bib['citation_lastpage']
    attribution = (f'{escape(item["version"])} · '
                   f'<a href="{escape(item["source_url"], quote=True)}">Source</a>')
    if item.get('license_url'):
        attribution += f' · <a rel="license" href="{escape(item["license_url"], quote=True)}">{escape(item["license_label"])}</a>'
    if item.get('note'):
        attribution += ' · ' + escape(item['note'])
    article = {'@context': 'https://schema.org', '@type': 'ScholarlyArticle',
               'headline': p['title'], 'author': [{'@type': 'Person', 'name': a} for a in p['authors']],
               'datePublished': bib['citation_publication_date'], 'abstract': item['abstract'],
               'url': base + 'paper.html', 'sameAs': p['links']['Paper'],
               'encoding': {'@type': 'MediaObject', 'contentUrl': base + 'paper.pdf', 'encodingFormat': 'application/pdf'}}
    structured = json.dumps(article, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(p['title'])} · Paper</title><meta name="description" content="{escape(p['summary'], quote=True)}">
<meta name="color-scheme" content="light dark"><link rel="canonical" href="{base}paper.html">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/scholar.css">
{metadata(p)}<script type="application/ld+json">{structured}</script></head>
<body><main><nav aria-label="Research navigation"><a href="/">Nousphera</a><a href="{base}">{escape(p['name'])} project ↗</a></nav>
<article><header><h1>{escape(p['title'])}</h1><p class="authors">{authors}</p><p class="publication">{escape(citation)}</p></header>
<section aria-labelledby="abstract-title"><h2 id="abstract-title">Abstract</h2><p class="abstract">{escape(item['abstract'])}</p></section>
<div class="links"><a class="download" href="paper.pdf">Read PDF</a><a href="{escape(p['links']['Paper'], quote=True)}">Publication ↗</a><a href="citation.bib">BibTeX</a></div>
<p class="source">{attribution}</p></article></main></body></html>
'''
