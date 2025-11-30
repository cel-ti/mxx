# System Patterns

## Architecture
- **Config system**: TOML files in `~/.mxx/configs/`
- **Naming**: `name.toml` (profile), `name.ld.toml` (LD), `name.maa.toml` (MAA)
- **Models**: BaseModel → LDModel, MaaModel, MxxProfile
- **Plugins**: Singleton loader, scoop path resolution
- **Templates**: Recursive `{"template": "name"}` references

## Core Components
- **config.py**: Path utilities
- **model_load.py**: Loading with caching
- **parser.py**: Validation (skips scoop: paths)
- **runner.py**: Profile execution with hooks
- **profile_resolver.py**: Centralized data access

See [details/sp_architecture_layers.md](details/sp_architecture_layers.md) for layered architecture.

## Data Models
- **LDModel**: `index` XOR `name`
- **MaaModel**: `path`, `app`, `configDir`, `fileConfig`, `parseConfig`
- **MxxProfile**: Optional `ld`/`maa`, `lifetime`, `waittime`

See [details/sp_models_full.md](details/sp_models_full.md) for complete specifications.

## Plugin System
- Singleton PluginLoader searches `mxxp_*` packages
- Discovery from installed + `cwd/plugins/`
- Hooks: pre_profile_start, post_profile_start, etc.
- Scoop plugin resolves `path = "scoop:app"` → actual path

See [details/sp_plugin_system.md](details/sp_plugin_system.md) for details.

## CLI Commands
```bash
mxx config new <name> [--template]  # Create from template
mxx config cat [name]                # List/display configs
mxx run up <profile> [--kill|--kill-all]  # Start profile
mxx run down [profile...]            # Kill processes
```

**Execution behavior**:
- Default: Start and return immediately
- `--kill`: Wait for `lifetime`, kill profile
- `--kill-all`: Wait for `lifetime`, kill all processes

## Atomic Functions
Small, testable functions:
- `get_model_type()`, `get_type_from_name()`, `is_profile_part()`
- `get_model_badge()`, `validate_model()`, `format_model_line()`

See [details/sp_atomic_patterns.md](details/sp_atomic_patterns.md).

## Utilities
- `utils/nofuss/toml.py` - TOML helpers
- `utils/kill.py` - Process termination
- `utils/subprocess.py` - Detached launching
