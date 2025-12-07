# mxx

Unified profile management for LD (LDPlayer) and MAA (MAA Assistant Arknights).

## Features

- **Unified Configuration**: Manage LD and MAA profiles in TOML format
- **Plugin System**: Extensible architecture with hooks for commands and profiles
- **Context Variables**: Pass runtime parameters via `--var` flags
- **Completion Tracking**: Prevent duplicate profile runs per day
- **Template System**: Create profiles from reusable templates
- **Path Resolution**: Automatic scoop path resolution for portable apps

## Installation

```bash
pip install -e .
```

## Quick Start

### Create a Profile

```bash
# Create from template
mxx config new myprofile --template profile

# Edit the generated config
# ~/.mxx/configs/myprofile.toml
```

### Run a Profile

```bash
# Start profile
mxx run up myprofile

# Start with completion tracking
mxx run up myprofile --var by-completion

# Start and auto-kill after lifetime
mxx run up myprofile --kill

# Kill all processes after lifetime
mxx run up myprofile --kill-all
```

### Manage Profiles

```bash
# List all profiles
mxx config cat

# View specific profile
mxx config cat myprofile

# Kill specific profile
mxx run down myprofile

# Kill all profiles
mxx run down
```

## Context Variables

Pass runtime parameters to plugins using `--var`:

```bash
# Boolean flags (auto-set to "true")
mxx run up profile --var by-completion
mxx run up profile --var debug

# Key-value pairs
mxx run up profile --var mode=production
mxx run up profile --var timeout=30

# Multiple variables
mxx run up profile --var by-completion --var reset-completion
```

### Built-in Variables

- `by-completion`: Enable completion tracking (skip if already run today)
- `reset-completion`: Reset completion status for profile

## Plugin System

Plugins extend mxx functionality through hooks:

### Profile Hooks
- `pre_profile_start(profile, ctx)` - Before profile starts
- `post_profile_start(profile, ctx)` - After profile starts
- `pre_profile_kill(profile, ctx)` - Before profile killed
- `post_profile_kill(profile, ctx)` - After profile killed

### Command Hooks
- `pre_command(command_name, ctx)` - Before command execution
- `post_command(command_name, ctx, result)` - After command success
- `command_error(command_name, ctx, error)` - On command error

### Creating a Plugin

```python
from mxx.plugin_system.plugin import MxxPlugin

class MyPlugin(MxxPlugin):
    def pre_profile_start(self, profile, ctx):
        vars = ctx.get('vars', {})
        profile_name = ctx.get('profile_name')
        
        if vars.get('my-flag') == 'true':
            print(f"Running {profile_name} with my-flag!")

plugin = MyPlugin()
```

Save as `mxxp_myplugin/__plugin__.py` and install:

```bash
pip install -e ./mxxp_myplugin
```

### Built-in Plugins

- **check-completion**: Track daily profile completions
- **check-single-instance**: Prevent multiple mxx instances
- **scoop**: Resolve scoop app paths
- **check-free**: Check LD console availability

## Configuration

Profiles use TOML format in `~/.mxx/configs/`:

```toml
# myprofile.toml
[ld]
index = 0

[maa]
path = "scoop:MAA"
app = "MAA"
configDir = "config"
fileConfig = "gui.json"
parseConfig = "release"

lifetime = 3600  # seconds
waittime = 15    # seconds between LD and MAA start
```

### Template References

```toml
# Inherit from template
{"template": "base"}

[maa]
path = "scoop:MAA"
```

### Scoop Path Resolution

```toml
# Automatically resolves to scoop install path
path = "scoop:MAA"
# Becomes: C:/Users/{user}/scoop/apps/MAA/current
```

## Development

### Project Structure

```
mxx/
├── src/mxx/
│   ├── cli/           # CLI commands
│   ├── core/          # Core logic
│   ├── models/        # Data models
│   ├── plugin_system/ # Plugin infrastructure
│   ├── templates/     # Config templates
│   └── utils/         # Utilities
├── plugins/           # Development plugins
│   ├── check-completion/
│   ├── check-single-instance/
│   └── scoop/
└── memory-bank/       # Project documentation
```

### Running Tests

```bash
pytest tests/
```

## License

MIT

