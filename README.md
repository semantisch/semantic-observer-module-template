# Semantic Observer module template

Build a small, independently versioned bot that proposes evidence-backed changes to a research knowledge graph. Use this repository as a GitHub template or clone it. It is shared-platform tooling: BilAI is one configuration, not a separate implementation.

**Status:** the executable reference module and its local contract tests work today. Public graph reading is live. Self-service module registration, contribution credentials and managed container execution are the next integration stage; this repository does not pretend those write endpoints already exist. It never modifies BKG directly.

## Run the example

Python 3.12 or later; no third-party packages are required.

```sh
python3 -m unittest discover -s tests -v
python3 -m observer_module.main < fixtures/person.json > proposal.json
```

The fixture is synthetic and must never be submitted as research evidence. The module finds a checksum-valid ORCID beside a person's name on an already verified profile URL. A random name match, conflicting identifiers or an existing fact produces no addition. Even a positive proposal requires a reviewer to inspect the relationship.

```sh
docker build -t observer-module-example .
docker run --rm -i --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --memory 128m --cpus .25 \
  observer-module-example < fixtures/person.json > proposal.json
```

A managed release must record the built image's immutable digest and source commit; a mutable tag is insufficient for registration. The example build uses a Python base tag for convenience. Pin its resolved digest in a reviewed production release.

## Read the live public graph

These endpoints already exist:

```sh
curl -fsS https://bkg.semantic.observer/api/v1/catalogue
curl -fsS https://bkg.semantic.observer/api/v1/ontology.ttl
curl -fsS https://bkg.semantic.observer/api/v1/openapi.json
```

Use the [MCP connection guide](https://bkg.semantic.observer/mcp-server) for research tools, or the [SPARQL editor](https://bkg.semantic.observer/sparql-query-service). Private instances require a workspace read token. Never put a token in the repository, prompt, output bundle or source URL.

## Adapt a module

1. Change `module.json`: identifier, repository, version, task, prerequisite assets, allowed predicates/actions and budgets.
2. Replace `propose()` with your narrow extraction or linking task. Any language can implement the same JSON-in / JSON-out contract; a Dagster installation is not required inside a module.
3. Add fixtures for ambiguity, conflicting identifiers, changed evidence, missing pages and retry/idempotency. Tests should demonstrate refusal to invent unsupported facts.
4. Produce proposals with pinned graph/crawl/ontology revisions, exact source-version and passage references, and a reason for each addition/removal.
5. Submit the repository and an immutable release for operator validation before requesting execution on the infrastructure. The operator records the approved source commit, image digest and capabilities. No self-service registration endpoint is currently published.

Read [the contract](docs/contract.md) and [integration plan](docs/integration.md). The proposed host will reuse Observer's existing reviewed change mechanism, source capture and provenance checks rather than granting bots raw SPARQL update access.
