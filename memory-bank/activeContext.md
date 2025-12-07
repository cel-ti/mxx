# Active Context
- **Current Status (Dec 6 2025):**
  - ✅ Architecture complete and tested
  - ✅ Enhanced plugin system with CLI command registration
  - ✅ Plugin hooks for command execution (pre/post/error)
  - ✅ Context variable system with `--var` arguments
  - ✅ Completion tracking plugin operational
  - ✅ All configs migrated to new format
  - System ready for production use

- **Latest Session (Dec 6 2025):**
  - Implemented process monitoring during profile lifetime
  - `sleep_with_countdown()` now checks LD (via ldpx) and MAA processes every 10s
  - Failure counter tracks consecutive failures (max 10)
  - Returns False on failure, sets `profile_failed=True` in context
  - Completion tracking now records success/failure status
  - JSON format: `{"profile": true}` (success) or `{"profile": false}` (failed)
  - By default, only successful runs prevent re-execution
  - `--var include-failed` flag to skip even if previous run failed
  - Auto-retry pattern: failed runs allow retry, successful runs skip
  - Dev-install script auto-bumps plugin micro versions

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
