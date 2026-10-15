import copy
import json
from pathlib import Path
import sys
import unittest
from xml.etree import ElementTree

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_projects as build
from research_icons import ICONS, GROUPS, research_icon
from research_visuals import numeric_value, validate_insight, diagram_markup, chart_markup, table_markup

class ResearchVisualTests(unittest.TestCase):
    def test_all_papers_have_audited_evidence_and_comparable_tables(self):
        projects=build.load_projects()
        self.assertEqual(len(projects),14)
        for p in projects:
            self.assertIn('insight',p,p['slug'])
            validate_insight(p['insight'],build.public_url)
            self.assertNotIn('/Users/',json.dumps(p['insight']))
            self.assertTrue(p['insight']['limitations'])
            html=build.project_page(p,projects)
            if p['slug'] == 'fedln':
                self.assertIn('data-fl-tour',html)
                self.assertIn('id="fl-algorithm-title"',html)
            else:
                self.assertIn('data-paper-story',html)
                self.assertIn('class="results-panel"',html)
            # Full evidence is retained in data; the page presents selected comparisons.
            from paper_results import load_results, selected_result
            for panel in load_results(p)['panels']:
                self.assertIn(build.esc(panel['source']['url']), html)
                if panel['kind'] == 'scatter': continue
                result = selected_result(p, panel)
                columns = panel.get('columns', list(range(len(result['columns'])-1))) if panel['kind'] == 'table' else sorted({c for chart in panel['charts'] for c in chart['columns']})
                for row in result['rows']:
                    for c in columns:
                        self.assertIn(build.esc(str(row['values'][c])), html)

    def test_icons_are_original_vector_markup_and_grouped_once(self):
        names=[n for values in GROUPS.values() for n in values]
        self.assertGreaterEqual(len(ICONS),70)
        self.assertEqual(len(names),len(set(names)))
        self.assertEqual(set(names),set(ICONS))
        for name in ICONS:
            svg=ElementTree.fromstring(research_icon(name))
            self.assertEqual(svg.attrib['viewBox'],'0 0 24 24')
            self.assertEqual(svg.attrib['stroke'],'currentColor')
        with self.assertRaises(ValueError): research_icon('<script>')

    def test_numeric_values_do_not_invent_results_from_ranges_or_missing_cells(self):
        self.assertEqual(numeric_value('87.2 ± 0.3'),87.2)
        self.assertEqual(numeric_value('10.2×'),10.2)
        self.assertIsNone(numeric_value('80–90'))
        self.assertIsNone(numeric_value('—'))
        self.assertIsNone(numeric_value('<1'))
        self.assertIsNone(numeric_value('10 (estimated)'))

    def test_chart_rejects_truncated_axes_and_out_of_range_values(self):
        records=[p['insight'] for p in build.load_projects() if p.get('insight')]
        self.assertTrue(records)
        d=copy.deepcopy(next(d for d in records if any(r.get('chart') for r in d['results'])))
        result=next(r for r in d['results'] if r.get('chart'))
        result['chart']['min']=50
        with self.assertRaises(ValueError):validate_insight(d,build.public_url)
        result['chart']['min']=0;result['chart']['max']=0.0001
        with self.assertRaises(ValueError):validate_insight(d,build.public_url)

    def test_alternative_diagrams_do_not_draw_sequential_arrows(self):
        d={'type':'alternatives','title':'Three choices','description':'Choose one','footnote':'Not a pipeline','stages':[{'title':x,'detail':'Details','location':'Client','icon':'model'} for x in ['A','B','C']]}
        html=diagram_markup(d,'test')
        self.assertNotIn('diagram-connector',html)
        d['type']='pipeline'
        self.assertEqual(diagram_markup(d,'test').count('class="diagram-connector"'),2)

    def test_visual_text_and_table_cells_are_escaped(self):
        d={'type':'pipeline','title':'<script>x</script>','description':'<img onerror=x>','footnote':'Safe','stages':[{'title':'<b>X</b>','detail':'<script>','location':'<b>','icon':'model'}]*2}
        html=diagram_markup(d,'test')
        self.assertNotIn('<script>',html);self.assertIn('&lt;script&gt;',html)
        r={'title':'A','context':'B','columns':['Method','Accuracy'],'rows':[{'label':'<b>','values':['<script>']} ]}
        self.assertNotIn('<script>',table_markup(r,'table'))

if __name__=='__main__':unittest.main()
