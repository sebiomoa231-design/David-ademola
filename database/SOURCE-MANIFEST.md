# Database source manifest

This manifest records the exact upstream commits copied into the David AI database section. The source trees are preserved as ordinary files under `database/`; their nested `.git` directories are not copied.

| Destination | Upstream | Commit | Tracked files at source | Copied files | Working-tree size at source |
|---|---|---|---:|---:|---:|
| `fastapi-backend-template/` | `Aeternalis-Ingenium/FastAPI-Backend-Template` | `d2e931b9639aa5fbca2a85c1711e47c8ee39b254` | 85 | 85 | 124.5 KiB |
| `fastapi-boilerplate/` | `benavlabs/FastAPI-boilerplate` | `2b6373d922bc993c7706c25a53f8dbab4e00217f` | 262 | 262 | 2.5 MiB |
| `pgvector/` | `pgvector/pgvector` | `36c26ba17644aeb63707f536287a0265c5309234` | 158 | 158 | 712.8 KiB |
| `supabase-postgres/` | `supabase/postgres` | `65a9da77021664ad2f20f6717ba63f2ebd9c5833` | 884 | 884 | 58.7 MiB |

The aggregate copied source-tree count is **1,389 files** before the David-specific database README, manifest, and placeholder files. No source repository reported Git submodules, generated cache directories, or files above GitHub’s 100 MiB hard limit during the audit. The largest source tree is `supabase-postgres/` at approximately 58.7 MiB.

## License records

The upstream license files remain in their copied locations: `fastapi-backend-template/LICENSE.md`, `fastapi-boilerplate/LICENSE.md`, `pgvector/LICENSE`, and `supabase-postgres/LICENSE`. They must be reviewed before redistribution, modification, or production packaging.

## Verification command

From the David repository root:

```bash
python3 database/scripts/verify_source_trees.py
```

## References

1. [Aeternalis-Ingenium/FastAPI-Backend-Template](https://github.com/Aeternalis-Ingenium/FastAPI-Backend-Template)
2. [benavlabs/FastAPI-boilerplate](https://github.com/benavlabs/FastAPI-boilerplate)
3. [pgvector/pgvector](https://github.com/pgvector/pgvector)
4. [supabase/postgres](https://github.com/supabase/postgres)
