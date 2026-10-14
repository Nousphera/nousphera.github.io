"""Export the project's original reusable SVG icons and public JSON inventory."""
from pathlib import Path
from html import escape as esc
import json
from research_icons import ICONS, GROUPS

ROOT = Path(__file__).resolve().parent.parent


def export_icons():
    folder=ROOT/'assets/research/icons'
    folder.mkdir(parents=True,exist_ok=True)
    for name,paths in ICONS.items():
        svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="{esc(name.replace('-',' '))}"><style>:root{{color:#34465d}}@media(prefers-color-scheme:dark){{:root{{color:#b6cae5}}}}</style>{paths}</svg>\n'''
        (folder/(name+'.svg')).write_text(svg)
    (ROOT/'assets/research/catalog.json').write_text(json.dumps({'grid':24,'stroke_width':1.6,'groups':GROUPS,'icons':[{'id':n,'file':f'/assets/research/icons/{n}.svg'} for n in ICONS]},indent=2)+'\n')


if __name__ == '__main__':
    export_icons()
    print(f'Exported {len(ICONS)} original SVG icons and assets/research/catalog.json')
