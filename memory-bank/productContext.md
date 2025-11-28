# Product Context
- **Problem Statement:** Power users juggling multiple MAA setups need a single CLI to register where configs live, snapshot or restore curated subsets, and script "auto" launch routines without manually editing TOML/JSON each time.
- **Target Users:** Windows operators running MAA + LDPlayer combos who prefer declarative TOML profiles and repeatable automation; secondary users are developers extending the CLI with plugins.
- **User Goals:**
  - Register profile and MAA config paths once, then reuse across commands.
  - Back up config folders with include/exclude controls, keeping secrets or bulky files out.
  - Restore configs safely with overwrite rules for environment-specific tweaks.
  - Define auto profiles (which emulator slot, wait time, lifetime, custom extras) and run them quickly.
  - Inspect and edit profile TOMLs using the bundled `open` helpers that jump into VS Code/Notepad.
- **Primary Workflows:**
  1. Use `mxx app config ...` to set global paths stored in `~/.mxx/config.json`.
  2. Place Maa profile TOMLs under `~/.mxx/maa` and auto profiles under `~/.mxx/profiles`; list/manage via `mxx maa` and `mxx auto` subcommands.
  3. Run `mxx maa backup/restore` to zip configs, leveraging wildcard-based field excludes or overwrites defined on each profile.
  4. Execute `mxx auto run <profile>` or generate schedules with filtering/sorting for batch automation.
  5. Reference the provided utilities programmatically when creating new plugins or scripted flows.
- **UX Considerations:** CLI output should stay human-readable (tables in `schedule`, pretty-printed configs in `info`), and commands must no-op gracefully when profiles are missing.
