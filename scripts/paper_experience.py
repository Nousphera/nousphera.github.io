"""FedLN reading standard, with paper-specific artwork and source-bound results."""
from html import escape as esc
import importlib
from xml.etree import ElementTree as ET

GROUPS = ('compression', 'audio', 'foundations', 'privacy', 'sdapt')
CONNECTED_STORIES = {
    'mpsl': 'One training step · Late fusion',
    'fedstar': 'One federated round · Audio',
    'fedser': 'One federated round · Speech',
    'fedcompress': 'Cluster · Distill · Adapt',
    'fedcode': 'Codebooks across clients and server',
    'ae-psl': 'Parallel split learning · Encoded features',
    'matu': 'Shared updates · Task-specific models',
    'enccluster': 'Compact updates · Encrypted aggregation',
    'efu': 'Encrypted federated unlearning',
    'fiba': 'Local poisoning · Global impact',
    'plix': 'Learn once · Recognize new words',
    'da-mldg': 'Learn across source domains',
    'sdapt': 'Adapt together · Specialize locally',
}
STORY_STYLES = {
    **{slug: slug for slug in ('mpsl', 'fedstar', 'fedser')},
    **{slug: 'compression' for slug in ('fedcompress', 'fedcode')},
    **{slug: 'foundation' for slug in ('ae-psl', 'matu')},
    **{slug: 'privacy' for slug in ('enccluster', 'efu', 'fiba')},
    **{slug: 'audio-method' for slug in ('plix', 'da-mldg')},
    'sdapt': 'sdapt',
}


def load_story(slug):
    for name in GROUPS:
        try:
            module = importlib.import_module('stories.' + name)
        except ModuleNotFoundError as error:
            if error.name != 'stories.' + name:
                raise
            continue
        if slug in module.STORIES:
            story = module.STORIES[slug]
            validate_story(story)
            return story
    return None


def inline(text):
    """Only editorial emphasis is allowed in prose, never arbitrary HTML."""
    root = ET.fromstring('<span>' + text + '</span>')
    for element in root.iter():
        if element.tag not in {'span', 'strong', 'em', 'sub', 'sup', 'code', 'br'} or element.attrib:
            raise ValueError('Unsupported story prose markup')
    return text


def validate_story(s):
    for key in ('overview', 'contributions', 'steps', 'method', 'takeaways'):
        if not s.get(key): raise ValueError('Story missing ' + key)
    inline(s['overview'])
    for value in s['contributions'] + s['takeaways'] + s.get('scope',[]) + s.get('result_leads',[]): inline(value)
    if not 3 <= len(s['steps']) <= 6: raise ValueError('Story needs 3–6 steps')
    for step in s['steps']:
        if not step.get('title') or not step.get('caption'): raise ValueError('Story step needs a title and caption')
        svg = ET.fromstring(step.get('art', step.get('svg', '')))
        if svg.tag.split('}')[-1] not in {'svg','div'} or not svg.get('aria-label'):
            raise ValueError('Story artwork needs an accessible description')
        duration = step.get('duration_ms', 6000)
        if not 5000 <= duration <= 20000: raise ValueError('Invalid scene duration')
        for element in svg.iter():
            if element.tag.split('}')[-1] in {'script','foreignObject','image','iframe','object','embed','style','link','img'}:
                raise ValueError('Story artwork must be self-contained vector markup')
            if any(k.startswith('on') for k in element.attrib): raise ValueError('Inline event handler')
            if 'data-reveal' in element.attrib and not 0 <= int(element.get('data-reveal')) < duration - 1000:
                raise ValueError('Artwork must be fully visible before a scene ends')
    for card in s['method']:
        inline(card['text'])
        if card.get('note'): inline(card['note'])
        if card.get('formula'):
            formula = ET.fromstring(card['formula'])
            if formula.tag != '{http://www.w3.org/1998/Math/MathML}math': raise ValueError('Use native MathML')


def tour_markup(p, s):
    buttons = ''.join(f'<button type="button" data-story-step="{i}" aria-pressed="{str(i==0).lower()}"><span>{i+1:02d}</span>{esc(step.get("short_title",step["title"]))}</button>' for i,step in enumerate(s['steps']))
    scenes = ''
    for i,step in enumerate(s['steps']):
        title = '' if step.get('title_in_art') else f'<strong>{esc(step["title"])}</strong>'
        scenes += f'<figure data-story-scene="{i}" data-story-duration="{step.get("duration_ms",6000)}"><div class="story-picture">{step.get("art", step.get("svg", ""))}</div><figcaption>{title}<span>{esc(step["caption"])}</span></figcaption></figure>'
    is_delta = p['slug'] == 'deltamask'
    connected = p['slug'] in CONNECTED_STORIES
    kind = f' data-story-kind="{esc(p["slug"])}"' if is_delta or connected else ''
    heading = CONNECTED_STORIES.get(p['slug'], 'One federated round · Mask updates' if is_delta else 'Inside '+p['name'])
    navigation_class = 'dm-navigation' if is_delta else 'story-navigation'
    navigation = f'<div class="{navigation_class}" data-story-navigation hidden><button type="button" data-story-prev aria-label="Previous animation step">← Previous</button><span data-story-counter>1 / {len(s["steps"])}</span><button type="button" data-story-next aria-label="Next animation step">Next →</button></div>' if is_delta or connected else ''
    css_class = 'paper-story connected-story' if connected else 'paper-story'
    return f'''<section class="{css_class}"{kind} data-paper-story data-running="false" aria-label="{esc(p['name'])} visual walkthrough">
<header class="story-head"><span class="px-kicker">{esc(heading)}</span><button type="button" class="story-toggle" data-story-toggle hidden><svg viewBox="0 0 20 20" aria-hidden="true"><path class="story-play-icon" d="m6 3 11 7-11 7Z"/><path class="story-pause-icon" d="M4 3h4v14H4zM12 3h4v14h-4z"/></svg><span data-story-toggle-label>Play overview</span></button></header>
<nav class="story-steps" aria-label="Explore the method" data-story-controls hidden>{buttons}</nav><div class="story-progress" aria-hidden="true"><span data-story-progress></span></div>
<div class="story-viewport">{scenes}<button type="button" class="story-expand" data-story-expand hidden aria-label="Expand current diagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/></svg>Expand diagram</button></div>{navigation}<span class="sr-only" role="status" data-story-status></span><dialog class="story-dialog" data-story-dialog aria-label="{esc(p['name'])} enlarged diagram"><header><span>Method diagram</span><button type="button" data-story-close aria-label="Close enlarged diagram">Close ×</button></header><p class="story-dialog-hint">Swipe across the diagram</p><div class="story-dialog-scroll" data-story-expanded tabindex="0" aria-label="Enlarged diagram; scroll horizontally on small screens"></div><p data-story-expanded-caption></p></dialog></section>'''


def overview_markup(p, s):
    source = p.get('abstract_source', {'url':p['provenance']['source_url']})
    note = '<p>'+esc(source['note'])+'</p>' if source.get('note') else ''
    contributions = ''.join(f'<li><span class="px-bullet">{i:02d}</span><p>{inline(text)}</p></li>' for i,text in enumerate(s['contributions'],1))
    return f'''<section id="overview" data-tab-panel class="px-panel"><div class="px-intro"><span class="px-kicker">At a glance</span><p class="px-lead">{inline(s['overview'])}</p></div>{tour_markup(p,s)}<section class="px-contributions" aria-label="Contributions"><h2>What this adds</h2><ul>{contributions}</ul></section><details class="px-details"><summary>Abstract</summary><div class="px-details-body"><p>{esc(p['abstract'])}</p>{note}<a href="{esc(source['url'])}">Read more ↗</a></div></details></section>'''


def method_markup(p, s, originals):
    cards=[]
    for i, card in enumerate(s['method'],1):
        formula = f'<div class="px-equation">{card["formula"]}</div>' if card.get('formula') else ''
        note = f'<p class="px-formula-note">{inline(card["note"])}</p>' if card.get('note') else ''
        extra = f'<div class="px-technical">{formula}{note}</div>' if formula or note else ''
        cards.append(f'<article class="px-method-card"><header><span>{i:02d}</span><h3>{esc(card["title"])}</h3></header><div class="px-method-body {"has-technical" if extra else ""}"><p>{inline(card["text"])}</p>{extra}</div></article>')
    source=p['insight']['evidence_inventory']
    source_label = source.get('link_label', 'Method details in the paper')
    return f'''<section id="method" data-tab-panel class="px-panel"><header class="px-section-heading"><span class="px-kicker">How it works</span><h2>{esc(p['name'])}</h2></header><div class="px-method-cards">{''.join(cards)}</div><p class="px-source"><a href="{esc(source['source_url'])}">{esc(source_label)} ↗</a></p>{originals}</section>'''
