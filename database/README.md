# David AI database and infrastructure

This directory is the database and infrastructure section of the existing David AI repository. It preserves complete recoverable source trees from the four repositories requested in the database integration directive. David AI remains the main application; these trees are source and infrastructure references that can be activated behind explicit service, container, or dependency boundaries without replacing David's existing frontend, backend, providers, memory, creative suite, connectors, or APIs.

## Preserved source repositories

| Destination | Upstream repository | Captured commit | Files copied | License record |
|---|---|---|---:|---|
| `fastapi-backend-template/` | [Aeternalis-Ingenium/FastAPI-Backend-Template](https://github.com/Aeternalis-Ingenium/FastAPI-Backend-Template) | `d2e931b9639aa5fbca2a85c1711e47c8ee39b254` | 85 | `LICENSE.md` |
| `fastapi-boilerplate/` | [benavlabs/FastAPI-boilerplate](https://github.com/benavlabs/FastAPI-boilerplate) | `2b6373d922bc993c7706c25a53f8dbab4e00217f` | 262 | `LICENSE.md` |
| `pgvector/` | [pgvector/pgvector](https://github.com/pgvector/pgvector) | `36c26ba17644aeb63707f536287a0265c5309234` | 158 | `LICENSE` |
| `supabase-postgres/` | [supabase/postgres](https://github.com/supabase/postgres) | `65a9da77021664ad2f20f6717ba63f2ebd9c5833` | 884 | `LICENSE` |

The copied trees include their directories, source files, SQL, migrations, Docker and deployment material, scripts, tests, documentation, dependency files, PostgreSQL configuration, and other tracked repository content. Nested `.git` directories are intentionally excluded from the destination copy because this repository records the source commit and provenance in this file rather than embedding four competing Git histories.

## Supporting directories

The empty directories below are reserved for David-specific database integration work and are tracked with `.gitkeep` files. They do not replace or alter the source repositories above.

```text
database/
├── fastapi-backend-template/  # complete recoverable source tree
├── fastapi-boilerplate/       # complete recoverable source tree
├── pgvector/                  # complete recoverable source tree
├── supabase-postgres/         # complete recoverable source tree
├── migrations/                # David-specific migrations
├── schema/                    # David-specific schema documentation or SQL
├── seeds/                     # safe development/test seed data
├── scripts/                   # database maintenance and verification scripts
└── docker/                    # database-only compose/container overlays
```

## Integration boundary

The current David application continues to use its existing storage and API contracts. The copied repositories are not imported into the base FastAPI process automatically, and no production database credentials are added by this commit. Any activation should be performed as a separately configured database service or explicitly reviewed dependency change, with environment-backed connection strings, migration ordering, backup/restore procedures, least-privilege roles, and tests executed before switching David runtime traffic.

The intended future mapping is users and permissions to the existing authentication domain; conversations, messages, memory, knowledge, embeddings, and semantic search to PostgreSQL plus pgvector; projects, tasks, learning, and decisions to David’s domain tables; and Creative Suite assets, generations, voice records, and relationships to durable media metadata. The mapping is documented here as an integration boundary, not as a claim that those tables are already deployed.

## Preservation and verification

The source trees were cloned with their upstream Git history in a quarantine workspace, audited for tracked-file counts, complete working-tree files, licenses, configuration files, submodules, generated directories, and maximum file size, then copied without overwriting existing David paths. No force-push, reset, branch deletion, or existing application-file deletion is part of this integration.

## References

1. [Aeternalis-Ingenium/FastAPI-Backend-Template](https://github.com/Aeternalis-Ingenium/FastAPI-Backend-Template)
2. [benavlabs/FastAPI-boilerplate](https://github.com/benavlabs/FastAPI-boilerplate)
3. [pgvector/pgvector](https://github.com/pgvector/pgvector)
4. [supabase/postgres](https://github.com/supabase/postgres)
