"""Local contract checks. Observer must repeat them against its own pinned data."""
import hashlib
import json
from urllib.parse import urlparse
PROTOCOL = 'observer-module/v1'
PINS = ('workspace', 'baseSnapshot', 'crawlSnapshot', 'ontologyRevision')
def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
def https(value):
    return isinstance(value, str) and urlparse(value).scheme == 'https' and bool(urlparse(value).hostname) and not urlparse(value).username
def validate_input(value):
    if value.get('protocol') != PROTOCOL or any(not https(value.get(k)) for k in PINS):
        raise ValueError('Expected supported protocol and pinned HTTPS graph identities')
    e = value.get('entity', {})
    if not https(e.get('id')) or not e['id'].startswith(value['workspace']+'/entity/') or not e.get('name'):
        raise ValueError('Entity must belong to this workspace')
    if not isinstance(e.get('profileUrls'), list) or not all(https(u) for u in e['profileUrls']):
        raise ValueError('Expected known profile URLs from the graph')
    seen = set()
    for source in value.get('sources', []):
        if not https(source.get('url')) or not https(source.get('pageVersion')) or not source['pageVersion'].startswith(value['workspace']+'/crawl/'):
            raise ValueError('Source must be an immutable capture in this workspace')
        for p in source.get('passages', []):
            key = (source['url'], p.get('id'))
            if key in seen or not p.get('id') or not isinstance(p.get('text'), str):
                raise ValueError('Passages need unique identities and exact text')
            seen.add(key)
    return value
def validate_proposal(bundle, task, manifest):
    validate_input(task)
    if bundle.get('protocol') != PROTOCOL or bundle.get('inputHash') != digest(task):
        raise ValueError('Proposal does not match its immutable input')
    if bundle.get('module') != {k: manifest[k] for k in ('id', 'version')} or any(bundle.get(k) != task[k] for k in PINS):
        raise ValueError('Stale input or foreign module/workspace')
    proposal = bundle.get('proposal', {})
    if proposal.get('entities') != [] or not isinstance(proposal.get('gaps'), list):
        raise ValueError('This example only edits an existing person')
    changes = proposal.get('changes', [])
    if not isinstance(changes, list) or len(changes) > manifest['limits']['maxChanges']:
        raise ValueError('Change budget exceeded')
    evidence = {(s['url'], p['id']): s for s in task.get('sources', []) for p in s['passages']}
    seen = set()
    for c in changes:
        if c.get('action') not in manifest['capabilities']['actions'] or c.get('predicate') not in manifest['capabilities']['predicates'] or c.get('subject') != task['entity']['id']:
            raise ValueError('Change exceeds declared scope')
        obj = c.get('object', {})
        if obj.get('kind') != 'iri' or not https(obj.get('value')):
            raise ValueError('Identity links must be HTTPS IRIs')
        if len(c.get('reason', '')) < 12 or not c.get('evidence'):
            raise ValueError('Every change needs justification and evidence')
        for ref in c['evidence']:
            source = evidence.get((ref.get('url'), ref.get('passageId')))
            if not source or ref.get('pageVersion') != source['pageVersion']:
                raise ValueError('Unknown or stale evidence')
        key = digest(c)
        if key in seen:
            raise ValueError('Duplicate change')
        seen.add(key)
    return bundle
