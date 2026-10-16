import copy
import json
from pathlib import Path
import unittest
from observer_module.main import propose, valid_orcid
from observer_module.contract import validate_proposal
ROOT = Path(__file__).resolve().parent.parent
class ModuleTests(unittest.TestCase):
    def setUp(self):
        self.task=json.loads((ROOT/'fixtures/person.json').read_text())
        self.manifest=json.loads((ROOT/'module.json').read_text())
    def test_verified_profile(self):
        result=propose(self.task,self.manifest)
        self.assertEqual(len(result['proposal']['changes']),1)
        self.assertEqual(result,propose(self.task,self.manifest))
        self.assertFalse(valid_orcid('0000-0002-1825-0098'))
    def test_unrelated_page_is_not_identity_proof(self):
        self.task['entity']['profileUrls']=['https://university.example/someone-else']
        self.assertEqual(propose(self.task,self.manifest)['proposal']['changes'],[])
    def test_ambiguous_identifiers_remain_unknown(self):
        self.task['sources'][0]['passages'][0]['text']+=' Collaborator https://orcid.org/0000-0001-5109-3700'
        self.assertEqual(propose(self.task,self.manifest)['proposal']['changes'],[])
    def test_existing_fact_is_idempotent(self):
        self.task['entity']['identifiers']=['https://orcid.org/0000-0002-1825-0097']
        self.assertEqual(propose(self.task,self.manifest)['proposal']['changes'],[])
    def test_missing_name(self):
        self.task['entity']['name']='Someone Else'
        self.assertEqual(propose(self.task,self.manifest)['proposal']['changes'],[])
    def test_scope_and_stale_evidence(self):
        result=propose(self.task,self.manifest)
        mutations=[lambda r:r.update(baseSnapshot='https://example.org/other'),lambda r:r['proposal']['changes'][0].update(subject='https://example.org/other'),lambda r:r['proposal']['changes'][0].update(predicate='https://schema.org/name'),lambda r:r['proposal']['changes'][0].update(action='remove'),lambda r:r['proposal']['changes'][0]['evidence'][0].update(pageVersion='https://example.org/stale'),lambda r:r['proposal']['changes'][0]['evidence'][0].update(passageId='invented')]
        for mutate in mutations:
            changed=copy.deepcopy(result);mutate(changed)
            with self.assertRaises(ValueError):validate_proposal(changed,self.task,self.manifest)
    def test_foreign_source(self):
        self.task['sources'][0]['pageVersion']='https://another.example/crawl/one'
        with self.assertRaises(ValueError):propose(self.task,self.manifest)
if __name__=='__main__':unittest.main()
