"""One public research catalog; paper pages keep their independent renderer."""
from html import escape
from pathlib import Path
from urllib.parse import urlparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://nousphera.github.io'
PHRASES = ['learns together.', 'adapts efficiently.', 'acts at the edge.']


def research_areas(projects):
    areas = json.loads((ROOT / 'data/research-areas.json').read_text())['areas']
    public = {p['slug'] for p in projects}
    mapped = {slug for area in areas for slug in area['papers']}
    if public != mapped or len({a['id'] for a in areas}) != len(areas):
        raise ValueError('Research areas must cover exactly the public paper catalog')
    return areas


def tile(p, areas, icon):
    from catalog_art import thumbnail
    memberships = [a['id'] for a in areas if p['slug'] in a['papers']]
    terms = [p['name'], re.sub(r'([a-z])([A-Z])', r'\1 \2', p['name']),
             p['title'], p['tagline'], p['summary'], p['category'], p['venue'],
             str(p['year']), p['type'], *p['authors'], *p['topics'], *p.get('keywords', [])]
    terms += [part for method in p['method'] for part in (method['title'], method['text'])]
    if p['slug'] == 'fedln':
        terms += ['NNC AKD NA-FedAvg']
    terms += [a['title'] for a in areas if a['id'] in memberships]
    short_venue = p['venue'].split(' · ')[0]
    secondary, secondary_dark = ('#227d78', '#78d5cb') if p['slug'] in {'ae-psl', 'efu', 'da-mldg'} else ('#79639d', '#c4aceb')
    code_url = p['links'].get('Code') or p['links'].get('Repository')
    code_icon = 'github' if code_url and urlparse(code_url).hostname == 'github.com' else 'code'
    code_link = f'<a href="{escape(code_url)}" aria-label="{escape(p["name"])} code">{icon(code_icon)}Code</a>' if code_url else ''
    return f'''<article class="research-tile" data-project="{p['slug']}" data-areas="{' '.join(memberships)}" data-search="{escape(' '.join(terms))}" style="--card-accent:{p['accent']};--card-accent-dark:{p['accent_dark']};--card-tint:{p['tint']};--card-secondary:{secondary};--card-secondary-dark:{secondary_dark}">
<a class="tile-main" href="/projects/{p['slug']}/" aria-labelledby="name-{p['slug']}" aria-describedby="description-{p['slug']}"><div class="tile-art">{thumbnail(p['slug'])}</div><div class="tile-copy"><div class="tile-topic">{escape(p['topics'][0])}</div><h4 id="name-{p['slug']}">{escape(p['name'])}{icon('arrow')}</h4><p id="description-{p['slug']}">{escape(p['tagline'].rstrip('.'))}</p></div></a>
<div class="tile-footer"><span class="tile-venue" title="{escape(p['type'] + ' · ' + p['venue'])}">{escape(short_venue)}</span><div class="tile-resources"><a href="{escape(p['links']['Paper'])}" aria-label="{escape(p['name'])} paper">{icon('paper')}Paper</a>{code_link}</div></div></article>'''


def home_page(projects, icon, theme_control, asset_url):
    projects = sorted(projects, key=lambda p: (-p['year'], p['name'].lower()))
    areas = research_areas(projects)
    buttons = ''.join(f'<button type="button" data-filter="{a["id"]}" aria-pressed="false">{escape(a["title"])}<span>{len(a["papers"])}</span></button>' for a in areas)
    years = sorted({p['year'] for p in projects}, reverse=True)
    sections = ''
    for year in years:
        group = [p for p in projects if p['year'] == year]
        sections += f'''<section class="year-group" data-project-year="{year}" data-visible-count="{len(group)}" id="year-{year}" aria-labelledby="title-{year}"><div class="year-heading"><h3 id="title-{year}">{year}</h3><span class="year-rule"></span><span data-year-count>{len(group):02d}</span></div><div class="research-grid">{''.join(tile(p, areas, icon) for p in group)}</div></section>'''
    jumps = ''.join(f'<a href="#year-{year}" data-year-link="{year}">{year}</a>' for year in years)
    pause = '<svg class="icon writing-pause" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M9 5v14M15 5v14"/></svg><svg class="icon writing-play" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="m8 5 11 7-11 7z"/></svg>'
    intro = 'Research in decentralized learning and efficient foundation models. Towards agentic AI at the edge.'
    css = ''.join(f'<link rel="stylesheet" href="{asset_url(f)}">' for f in ['assets/projects.css', 'assets/research-home.css'])
    scripts = ''.join(f'<script src="{asset_url(f)}" defer></script>' for f in ['assets/projects.js', 'assets/catalog-filter.js', 'assets/hero-writing.js'])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Noösphere — Collaborative intelligence at the edge</title><meta name="description" content="{intro}"><meta name="color-scheme" content="light dark"><link rel="canonical" href="{ORIGIN}/"><meta property="og:title" content="Noösphere — Collaborative intelligence at the edge"><meta property="og:description" content="{intro}"><meta property="og:type" content="website"><meta property="og:url" content="{ORIGIN}/"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><script src="{asset_url('assets/theme.js')}"></script>{css}{scripts}</head>
<body class="research-home"><a class="skip" href="#collection">Skip to projects</a><header class="home-header"><a class="home-brand" href="/" aria-label="Noösphere home"><span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>Noösphere</a><nav aria-label="Main navigation"><a class="home-profile" aria-label="About me" href="https://vtsouval.github.io/">{icon('person')}<span>About me</span></a>{theme_control()}</nav></header>
<main id="main" class="home-main"><section class="home-hero" data-writing-hero data-phrases="{escape(json.dumps(PHRASES))}" aria-labelledby="home-title"><div class="hero-topline"><p class="home-eyebrow"><span></span>Research &amp; open source</p><button class="writing-toggle" type="button" data-writing-toggle aria-label="Pause headline animation" hidden>{pause}<span data-writing-label>Pause</span></button></div><h1 id="home-title"><span>Intelligence that</span><span class="writing-line" aria-hidden="true"><span data-writing-text>{PHRASES[0]}</span><span class="writing-caret"></span></span><span class="sr-only">learns together, adapts efficiently, and moves towards agency at the edge.</span></h1><p class="home-description">Research in <strong>decentralized learning</strong> and <strong>efficient foundation models.</strong><br> Towards agentic AI at the edge.</p></section>
<section id="collection" data-unified-catalog aria-labelledby="collection-title"><div class="catalog-heading"><h2 id="collection-title">Research projects<span>{len(projects):02d}</span></h2><nav class="year-jumps" aria-label="Browse projects by year">{jumps}</nav></div><div class="catalog-tools"><div class="catalog-control-row"><div class="catalog-filters" role="group" aria-label="Filter by research area" hidden><button type="button" data-filter="all" aria-pressed="true">All<span>{len(projects)}</span></button>{buttons}</div><label class="catalog-search">{icon('search')}<span class="sr-only">Search projects</span><input type="search" id="catalog-search" placeholder="Search papers, methods…" autocomplete="off" disabled></label></div><div class="catalog-status"><p id="catalog-status" role="status" aria-live="polite">{len(projects)} projects</p><button type="button" data-reset-projects hidden>{icon('close')}Clear filters</button></div></div><div class="year-collection">{sections}</div><div class="catalog-empty" hidden><h3>No matching projects</h3><p>Try another term or clear the filters.</p><button type="button" data-empty-reset>Show all projects {icon('arrow')}</button></div></section></main>
<footer class="home-footer"><a class="home-brand" href="/">Noösphere</a><span>Ideas into open research.</span><nav aria-label="Contact and profiles"><a href="https://github.com/Nousphera">{icon('github')}GitHub</a><a href="https://vtsouval.github.io/">{icon('person')}About me</a><a href="mailto:nousphera@proton.me">Email</a></nav></footer></body></html>\n'''


def legacy_gallery(asset_url):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Projects · Noösphere</title><meta name="robots" content="noindex,follow"><link rel="canonical" href="{ORIGIN}/"><script src="{asset_url('assets/catalog-redirect.js')}"></script><link rel="stylesheet" href="{asset_url('assets/projects.css')}"></head><body><main style="max-width:640px;margin:15vh auto;padding:24px"><h1>Noösphere projects</h1><p>The research catalog is now on the home page.</p><a href="/#collection">Continue to the project catalog →</a></main></body></html>\n'''
