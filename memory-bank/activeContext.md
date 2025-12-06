# Active Context
- **Current Status (Nov 29 2025):**
  - ✅ Architecture complete and tested
  - ✅ Plugin system working (scoop plugin resolves paths)
  - ✅ All configs migrated to new format
  - System ready for production use

- **Latest Session:**
  - Fixed scoop plugin to use `maa.path` instead of `maa.directory`
  - Added plugin discovery from `cwd/plugins/` directory
  - Installed plugins in editable mode for development
  - Corrected `--kill` vs `--kill-all` behavior in `run up`
  - Migrated all job configs to new profile format
  - Removed vestigial `[profile]` sections from templates

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
