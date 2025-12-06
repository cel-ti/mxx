# MXX Plugin Example

**Comprehensive reference implementation demonstrating all MXX plugin capabilities.**

This plugin serves as documentation and a starting point for creating your own plugins.

## Features Demonstrated

### ✅ Plugin Lifecycle
- **`init()`** - Plugin initialization
- State management within plugin

### ✅ CLI Command Registration
- **`register_commands(cli_group)`** - Add custom commands
- Top-level commands: `mxx example`
- Command groups: `mxx demo info`, `mxx demo echo`
- Command options and arguments

### ✅ Command Execution Hooks
- **`hook_pre_command(command_name, ctx)`** - Before any command
- **`hook_post_command(command_name, ctx, result)`** - After success
- **`hook_command_error(command_name, ctx, error)`** - On failure
- Access to Click context and parameters

### ✅ Profile Execution Hooks
- **`pre_profile_start(profile, ctx)`** - Before profile starts
- **`post_profile_start(profile, ctx)`** - After profile starts
- **`pre_profile_kill(profile, ctx)`** - Before profile killed
- **`post_profile_kill(profile, ctx)`** - After profile killed
- Access to profile configuration (LD, MAA)

### ✅ Profile Validation
- **`can_run_profile(profile, ctx)`** - Control execution
- **`can_kill_profile(profile, ctx)`** - Control termination
- Veto power (return False prevents action)

### ✅ Profile Contribution
- **`get_profiles()`** - Provide dynamic profiles
- Programmatic profile generation

### ✅ Custom Hook System
- **`hook(hook_name, *args, **kwargs)`** - Generic dispatcher
- Custom hooks: `hook_pre_ld_start`, `hook_pre_maa_launch`
- Plugin-to-plugin communication

## Installation

```bash
cd plugins/example
uv pip install -e .
```

## Usage Examples

### Custom Commands

```bash
# Run example command
mxx example
mxx example --verbose

# Use demo group
mxx demo info
mxx demo echo "Hello World"
```

### With Existing Commands

```bash
# Hooks fire on any command
mxx config cat
# [ExamplePlugin] Pre-command: cat
# [ExamplePlugin] Post-command: cat completed successfully

# Hooks fire on profile execution
mxx run up myprofile
# [ExamplePlugin] Starting profile: myprofile
# [ExamplePlugin] Profile started successfully
```

## Plugin Structure

```
mxxp_plugin_example/
├── pyproject.toml          # Package metadata, dependencies
├── README.md               # Documentation
└── src/
    └── mxxp_plugin_example/
        ├── __init__.py     # Package entry
        └── __plugin__.py   # Plugin implementation (REQUIRED)
```

## Key Concepts

### 1. Naming Convention
- Package: `mxxp-*` (hyphen for PyPI)
- Module: `mxxp_*` (underscore for import)
- Loader discovers all `mxxp_*` packages

### 2. Plugin Instance
```python
plugin = ExamplePlugin()  # REQUIRED - exact name
```

### 3. Hook Execution Order
```
1. init() - once at startup
2. register_commands() - once at startup
3. pre_command → command → post_command - per command
4. pre_profile_start → profile → post_profile_start - per profile
```

### 4. Context Objects

**Click Context (`ctx`):**
- `ctx.params` - Command parameters
- `ctx.obj['plugin_loader']` - Access plugin loader
- `ctx.parent` - Parent command context

**Profile Context (`ctx: Dict`):**
- Runtime variables
- Shared state between hooks
- Custom plugin data

### 5. Veto Pattern

```python
def can_run_profile(self, profile, ctx):
    if not meets_requirements():
        return False  # Prevents ALL plugins from running
    return True
```

If **any** plugin returns `False`, action is blocked.

### 6. Hook Layering

Multiple plugins can hook the same event:
```
[Plugin A] Pre-command
[Plugin B] Pre-command
→ Command executes
[Plugin A] Post-command
[Plugin B] Post-command
```

Order determined by plugin load order.

## Common Patterns

### Logging Plugin
```python
def hook_pre_command(self, command_name, ctx):
    log.info(f"Command: {command_name}, User: {os.getenv('USER')}")
```

### Metrics Plugin
```python
def hook_post_command(self, command_name, ctx, result):
    metrics.increment(f"command.{command_name}.success")
```

### Policy Enforcement
```python
def can_run_profile(self, profile, ctx):
    if not check_quota(profile):
        click.echo("Quota exceeded")
        return False
    return True
```

### Environment Setup
```python
def pre_profile_start(self, profile, ctx):
    setup_logging()
    initialize_monitoring()
    ctx['start_time'] = time.time()
```

## Testing Your Plugin

1. **Install in development mode:**
   ```bash
   cd your-plugin
   uv pip install -e .
   ```

2. **Verify loading:**
   ```bash
   mxx --help  # Should show your commands
   ```

3. **Test hooks:**
   ```bash
   mxx your-command  # Watch for hook output
   ```

4. **Test with profiles:**
   ```bash
   mxx run up someprofile  # Check profile hooks
   ```

## Debugging

Enable verbose output to see plugin loading:
```python
# In plugin loader
print(f"Loaded plugin: {name}")
print(f"Warning: Failed to load plugin {name}: {e}")
```

## Best Practices

1. **Keep init() fast** - No heavy operations
2. **Handle errors gracefully** - Don't crash other plugins
3. **Use descriptive output** - Prefix with `[PluginName]`
4. **Document context usage** - What you add/expect in ctx
5. **Test hook combinations** - With other plugins installed
6. **Return True by default** - For `can_*` methods
7. **Fail safely** - Empty `get_profiles()` if generation fails

## See Also

- **check-single-instance** - Simple init() example
- **check-free** - can_run_profile() example  
- **scoop** - pre_profile_start() path resolution
- **test-command** - register_commands() basic
- **test-command-override** - Hook layering example

## License

Same as MXX project.
