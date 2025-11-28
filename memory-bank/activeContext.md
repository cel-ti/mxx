# Active Context
- **Current Focus:**
  - Establish baseline documentation for the project so future tasks can reference architecture and workflows quickly.
  - Keep config/backup utilities stable while expanding CLI ergonomics (e.g., scheduling filters, editor helpers).
- **Recent Changes (Nov 27 2025):**
  - Created the initial memory bank capturing scope, product intent, tech stack, and system patterns.
  - Verified supporting utilities via unit tests (file IO, nested keys, pattern matching) remain green.
- **Immediate Next Steps:**
  1. Add coverage for CLI/manager flows (mock filesystem + Click runner) to guard regressions.
  2. Fix `MxxMgr.save_config` to serialize BaseModel data via `.model_dump()` before writing JSON.
  3. Flesh out the dormant `plugin_system` namespace or remove it to avoid confusion.
  4. Document README usage examples so new operators can bootstrap quickly.
- **Risks / Watch Items:**
  - Windows-specific assumptions (LDPlayer CLI, `os.startfile`) limit portability; need abstraction if Linux/macOS support becomes a goal.
  - Optional process utilities silently unavailable without extras; consider user-facing guidance when commands rely on them.
