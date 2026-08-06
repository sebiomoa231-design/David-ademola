from __future__ import annotations

from app.services.memory_engine import MemoryEngine

# Backward-compatible alias: MemoryService is the original name used by
# routes/tests; MemoryEngine is the expanded implementation with search,
# relevance ranking, and learning support.
MemoryService = MemoryEngine
