# Active Context
- **Current Status (Dec 6 2025):**
  - ✅ Architecture complete and tested
  - ✅ Enhanced plugin system with CLI command registration
  - ✅ Plugin hooks for command execution (pre/post/error)
  - ✅ All configs migrated to new format
  - System ready for production use

- **Latest Session:**
  - Implemented custom Click classes (PluginAwareCommand, PluginAwareGroup)
  - Added `register_commands()` to PluginInterface for CLI extensibility
  - Added command execution hooks: pre_command, post_command, command_error
  - Created single-instance checker plugin (plugins/check-single-instance)
  - Created test plugins (plugins/test-command, plugins/test-command-override)
  - Created comprehensive example plugin at root (/example) for documentation
  - All CLI commands now plugin-aware with context passing

- **Current Behavior:**
  - `mxx run up <profile>` - Start and return immediately
  - `mxx run up <profile> --kill` - Wait for lifetime, kill profile
  - `mxx run up <profile> --kill-all` - Wait for lifetime, kill all processes
  - `mxx run down [profile...]` - Kill specific or all profiles
  - `mxx config cat` - Validates and displays configs with scoop path support

- **Active Configs:**
  - `~/.mxx/configs/` - Main profiles (maa, maag with LD index 2/3)
  - `~/.mxx/jobs/` - Scheduled profiles (gf2_cn, gf2_gl, re1999_cn, re1999_na)
  - All using scoop plugin for path resolution
