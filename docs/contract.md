# Reference contract v1

A module consumes one UTF-8 JSON object on standard input and emits one JSON object on standard output. Diagnostics go to standard error. Exit zero means a review bundle was produced, including a legitimate empty proposal; it does not mean changes were accepted. The process must stop within its declared budget.

`module.json` declares prerequisites and capabilities. The input fixes `workspace`, `baseSnapshot`, `crawlSnapshot` and `ontologyRevision`. The selected entity has its existing graph IRI, name, verified profile URLs and known identifiers. Each supplied source has a canonical URL, immutable `pageVersion` IRI and exact passages with stable IDs. The host may additionally provide headings, links, structured data, page classes and every classification score from the versioned crawl.

The output repeats those pins and the module identity/version. `inputHash` is SHA-256 over the reference validator's UTF-8 JSON serialization (sorted keys, no indentation or ASCII escaping). It is a repeatability check, not an authorization mechanism or digital signature. The host records the approved repository commit, image digest, actual run identity and execution times independently; a module cannot attest those facts about itself.

Each proposed change has:

- `action`: `add` or an explicitly permitted `remove`;
- `subject`, `predicate`, and a typed RDF `object`;
- a human-readable `reason` explaining the addition or correction;
- evidence references containing `url`, immutable `pageVersion` and `passageId`.

The host resolves evidence references to its own captured text, quotations and positions; it never trusts a module to invent or rewrite a quotation. A new external page must first be captured and mapped through Observer's source broker. Search snippets alone are discovery hints. A PDF remains in administrator-only storage and is not copied into the source graph.

`proposal.entities` is empty in this example. A future module allowed to introduce entities must supply declared types, names, identity evidence and references that pass the host schema. `gaps` records ambiguity, unavailable providers and unsupported fields. Missing evidence must not become a guessed value.

This example allows only ORCID identity-link additions on the selected person. Its validator rejects other subjects, predicates, actions, stale versions, fabricated passages and duplicate changes. It does not prove semantic truth: the source relationship still needs review. Template checks supplement the host's authorization, identity, RDF, SHACL/ShEx, stale-input and provenance checks.
