## graphify

`graphify-out/` holds a knowledge graph of this repository. It is gitignored, so build it with
`/graphify .` if it is missing.

- Question about the repository, and `graphify-out/graph.json` exists: `graphify query "<question>"`
  before grep. Also `graphify path "<A>" "<B>"` and `graphify explain "<concept>"`.
- `graphify-out/GRAPH_REPORT.md` only when those three do not surface enough.
- After changing files: `graphify update .` (AST-only, no API cost).
