# Tech Context

## Language & Runtime
- **Python 3.12+** required
- **Windows-focused**: Uses Windows-specific APIs and LDPlayer CLI
- **Type hints**: Full typing with dataclasses

## Core Dependencies
- **click >= 8.3.1** - CLI framework
- **psutil >= 7.1.3** - Process management
- **toml >= 0.10.2** - TOML parsing
- **Standard library**: pathlib, dataclasses, typing, importlib, pkgutil

## Development Tools
- **pytest >= 9.0.1** - Testing framework (57 tests)
- **uv_build** - Build backend
- **ldpx >= 0.3.0** - LDPlayer interaction (dev dependency)

## Packaging
- **Entry point**: `mxx = mxx.cli.main:cli` (updated from old `mxx.click.main:cli`)
- **Module execution**: `python -m mxx` via `__main__.py`
- **Build system**: uv_build >= 0.9.11

## Testing
- **57 comprehensive tests**:
  - 34 tests for models (BaseModel, LDModel, MaaModel, MxxProfile)
  - 23 tests for config/loading (paths, discovery, templates, caching)
- **Test files**: `tests/test_models.py`, `tests/test_config_and_load.py`
- **Coverage**: Models, config loading, template resolution, validation

## Filesystem Layout (New)
```
~/.mxx/
  configs/              # All profile configs
    profile.toml        # Full profiles (MxxProfile)
    profile.ld.toml     # LD-only configs (LDModel)
    profile.maa.toml    # MAA-only configs (MaaModel)

src/mxx/
  cli/                  # CLI commands
    main.py             # Entry point
    config.py           # Config management commands
    run.py              # Profile execution commands
    __init__.py
  core/                 # Core functionality
    config.py           # Path utilities
    model_load.py       # Loading with template support
    parser.py           # Validation logic
    runner.py           # Profile execution
    profile_resolver.py # Centralized resolution
  models/               # Data models
    base.py             # BaseModel foundation
    ld.py               # LDModel
    maa.py              # MaaModel  
    profile.py          # MxxProfile
  plugin_system/        # Plugin framework
    interface.py        # PluginInterface
    plugin.py           # MxxPlugin
    loader.py           # PluginLoader (singleton)
    __init__.py
  templates/            # TOML templates
    profile.template.toml
    maa.template.toml
    ld.template.toml
  utils/                # Utilities
    nofuss/
      toml.py           # TOML helpers
      json.py           # JSON helpers
      resolveEditor.py  # Editor launcher
      subprocess.py     # Process launching
    kill.py             # Process termination
```

## Execution Flow
1. **CLI invocation**: `mxx` → `cli.main:cli()`
2. **Command routing**: click dispatches to config/run subcommands
3. **Profile resolution**: ProfileResolver checks plugins then files
4. **Loading**: model_load.py handles TOML parsing and templates
5. **Validation**: parser.py validates models before execution
6. **Execution**: ProfileRunner launches with plugin hooks
7. **Process management**: Detached processes for MAA, ldpx CLI for LD

## Plugin Discovery
- Searches installed packages with `mxxp_*` prefix
- Imports `{package}.__plugin__` module
- Expects `plugin` attribute with MxxPlugin instance
- Singleton pattern ensures one-time discovery

## Performance Optimizations
- **Lazy loading**: Plugin profiles loaded on first access
- **Caching**: model_load.py caches parsed models
- **Singleton**: PluginLoader instantiated once
- **Atomic functions**: Small, reusable, testable components

## Windows-Specific
- **Editor**: Prefers VS Code (`code.cmd`), falls back to notepad
- **Processes**: Detached launch via Windows process flags
- **Paths**: Uses pathlib with Windows path handling
- **LDPlayer**: Invoked via `ldpx console launch/quit` CLI

## Code Organization Principles
- **Separation of concerns**: Data access (ProfileResolver) vs presentation (CLI)
- **Single responsibility**: Each function has one clear purpose
- **Pure functions**: Stateless helpers for type detection, formatting
- **Composition**: Small functions combine to build complex behavior
