"""Read a pinned task on stdin; emit a review bundle. No network or graph writes."""
import json
from pathlib import Path
import re
import sys
from .contract import PROTOCOL, PINS, digest, validate_input, validate_proposal
PATTERN = re.compile(r'https://orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])(?![\dA-Za-z-])')
def valid_orcid(identifier):
    total = 0
    for digit in identifier.replace('-', '')[:-1]: total = (total + int(digit)) * 2
    check = (12 - total % 11) % 11
    return identifier[-1] == ('X' if check == 10 else str(check))
def propose(task, manifest):
    validate_input(task)
    entity, found = task['entity'], {}
    for source in task.get('sources', []):
        # A random page sharing a name is insufficient identity evidence.
        if source['url'] not in entity['profileUrls']: continue
        for p in source['passages']:
            if entity['name'].casefold() not in p['text'].casefold(): continue
            for m in PATTERN.finditer(p['text']):
                if valid_orcid(m.group(1)):
                    found.setdefault(m.group(0), []).append({'url': source['url'], 'pageVersion': source['pageVersion'], 'passageId': p['id']})
    changes, gaps = [], []
    if len(found) > 1:
        gaps.append('Several ORCIDs occur in the known profile evidence; identity needs review.')
    elif len(found) == 1:
        identifier, evidence = next(iter(found.items()))
        if identifier not in entity.get('identifiers', []):
            changes.append({'action': 'add', 'subject': entity['id'], 'predicate': 'https://schema.org/sameAs', 'object': {'kind': 'iri', 'value': identifier}, 'reason': 'The previously verified profile names this person beside a checksum-valid ORCID. Review the relationship before acceptance.', 'evidence': evidence})
    else:
        gaps.append('No unambiguous checksum-valid ORCID is beside the person name on a known profile.')
    bundle = {'protocol': PROTOCOL, 'module': {k: manifest[k] for k in ('id', 'version')}, 'inputHash': digest(task), **{k: task[k] for k in PINS}, 'proposal': {'entities': [], 'changes': changes, 'gaps': gaps, 'providerChecks': []}}
    return validate_proposal(bundle, task, manifest)
def main():
    raw = sys.stdin.buffer.read(2_000_001)
    if len(raw) > 2_000_000: raise ValueError('Input exceeds the 2 MB budget')
    manifest = json.loads((Path(__file__).resolve().parent.parent/'module.json').read_text())
    print(json.dumps(propose(json.loads(raw), manifest), ensure_ascii=False, indent=2))
if __name__ == '__main__':
    try: main()
    except (ValueError, KeyError, TypeError) as error:
        print('Invalid module task: '+str(error), file=sys.stderr)
        sys.exit(2)
