# Progress

## Completed (Nov 29 2025)

### **Core Architecture**
✅ Unified TOML config system (90% code reduction)
✅ Composable parts: `name.toml`, `name.ld.toml`, `name.maa.toml`
✅ Template system with recursive resolution
✅ Models: BaseModel, LDModel, MaaModel, MxxProfile
✅ 57 comprehensive tests passing

### **Core Components**
✅ `core/config.py` - Path resolution
✅ `core/model_load.py` - Loading with caching
✅ `core/parser.py` - Validation (skips scoop paths)
✅ `core/runner.py` - ProfileRunner with plugin hooks
✅ `core/profile_resolver.py` - Centralized resolution

### **Plugin System**
✅ Singleton PluginLoader with cwd/plugins support
✅ Scoop plugin resolves `scoop:app_name` paths
✅ Profile hooks: pre_profile_start, post_profile_start, pre_profile_kill, post_profile_kill
✅ Command hooks: pre_command, post_command, command_error
✅ CLI command registration via `register_commands(cli_group)`
✅ Custom Click classes (PluginAwareCommand, PluginAwareGroup)
✅ Context passing with plugin_loader in ctx.obj
✅ Editable plugin installation for development

### **CLI Commands**
✅ `mxx config new/cat` - Config management
✅ `mxx run up [--kill|--kill-all]` - Profile execution
✅ `mxx run down [profiles...]` - Process termination

### **Working Features**
✅ Scoop plugin path resolution
✅ Profile lifetime with optional auto-kill
✅ Plugin discovery from local and installed packages
✅ Config validation with plugin path support
✅ All production configs migrated

### **Plugins Installed**
✅ mxxp-scoop - Resolves scoop app paths
✅ mxxp-check-free - Prevents runs during fullscreen/high activity
✅ mxxp-check-single-instance - Ensures only one MXX instance runs
✅ mxxp-test-command - Example: adds test command
✅ mxxp-test-command-override - Example: extends test command via hooks

## Current State
- System tested and working in production
- 4 main profiles configured (maa, maag)
- 4 job profiles configured (gf2_cn, gf2_gl, re1999_cn, re1999_na)
- All using scoop plugin for MAA path resolution

## Outstanding
- Scheduling system for job profiles
- Additional plugin examples
- Integration test coverage
