# Active Context
- **Current Status (Dec 6 2025):**
  - ✅ Architecture complete and tested
  - ✅ Enhanced plugin system with CLI command registration
  - ✅ Plugin hooks for command execution (pre/post/error)
  - ✅ Context variable system with `--var` arguments
  - ✅ Completion tracking plugin operational
  - ✅ All configs migrated to new format
  - System ready for production use

- **Latest Session:**
  - Implemented `--var` argument extraction before Click processing
  - Created `arg_extract.py` to parse `--var key=value` or `--var flag` (boolean=true)
  - Context stored in PluginLoader and passed to all hooks
  - Created completion tracking plugin (plugins/check-completion)
  - Completion plugin prevents duplicate profile runs per day
  - Added `--var by-completion` flag to enable completion tracking
  - Added `--var reset-completion` flag to reset completion status
  - Context includes vars and profile_name available to all plugins

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
