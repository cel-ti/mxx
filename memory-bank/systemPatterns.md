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
- **Profile hooks**: pre_profile_start, post_profile_start, pre_profile_kill, post_profile_kill
- **Command hooks**: pre_command, post_command, command_error
- **CLI extension**: `register_commands(cli_group)` for adding commands
- **Custom Click classes**: PluginAwareCommand, PluginAwareGroup wrap all commands
- **Context system**: 
  - `--var` args extracted before Click processing (`arg_extract.py`)
  - Context stored in PluginLoader.context with vars and profile_name
  - All hooks receive merged context dictionary
  - Boolean flags: `--var flag` → `flag=true`, `--var key=value` → `key: value`
- Scoop plugin resolves `path = "scoop:app"` → actual path
- **Completion tracking**: plugins/check-completion prevents duplicate daily runs
- **Example plugins**: /plugins/ for development, /example/ for comprehensive documentation

See [details/sp_plugin_system.md](details/sp_plugin_system.md) for details.

## CLI Commands
```bash
mxx config new <name> [--template]  # Create from template
mxx config cat [name]                # List/display configs
mxx run up <profile> [--kill|--kill-all] [--var KEY=VALUE]  # Start profile
mxx run down [profile...]            # Kill processes
```

**Execution behavior**:
- Default: Start and return immediately
- `--kill`: Wait for `lifetime`, kill profile
- `--kill-all`: Wait for `lifetime`, kill all processes

**Context variables** (`--var` flags):
- `--var by-completion`: Enable completion tracking (skip if already completed today)
- `--var reset-completion`: Reset completion status for profile
- `--var KEY=VALUE`: Pass custom key-value pairs to plugins
- `--var FLAG`: Boolean flag (automatically set to "true")

## Atomic Functions
Small, testable functions:
- `get_model_type()`, `get_type_from_name()`, `is_profile_part()`
- `get_model_badge()`, `validate_model()`, `format_model_line()`

See [details/sp_atomic_patterns.md](details/sp_atomic_patterns.md).

## Utilities
- `utils/nofuss/toml.py` - TOML helpers
- `utils/kill.py` - Process termination
- `utils/subprocess.py` - Detached launching
