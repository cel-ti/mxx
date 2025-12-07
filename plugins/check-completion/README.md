# MXX Check Completion Plugin

Tracks profile completions per day to prevent duplicate runs.

## Features

- **Daily completion tracking** - Uses `~/.mxx/completion/{date}.json` to track completions
- **Success/Failure tracking** - Records `true` for successful runs, `false` for failed runs
- **Opt-in behavior** - Only activates with `--var by-completion`
- **Smart skipping** - By default, only skips if previous run was successful
- **Include failed runs** - Use `--var include-failed` to skip even if previous run failed
- **Automatic recording** - Marks completion (success or failure) after profile runs
- **Reset capability** - Reset completion status with `--var reset-completion`
- **Boolean flag support** - Use `--var by-completion` (no `=true` needed)

## Installation

### From Git Repository

```bash
pip install git+https://github.com/cel-ti/mxx.git#subdirectory=plugins/check-completion
```

### Development Installation

```bash
cd plugins/check-completion
pip install -e .
```

## Usage

### Normal Run (No Tracking)
```bash
mxx run up myprofile
# Runs normally, no completion tracking
```

### With Completion Tracking
```bash
# Boolean flag syntax (recommended)
mxx run up myprofile --var by-completion

# Explicit value syntax (also works)
mxx run up myprofile --var by-completion=true

# First run (successful): 
# [CheckCompletion] Profile 'myprofile' not yet completed today.
# [CheckCompletion] Will track completion after run.
# ... profile runs ...
# [CheckCompletion] Marked 'myprofile' as completed successfully for today.

# Second run same day (after success):
mxx run up myprofile --var by-completion
# [CheckCompletion] Profile 'myprofile' already completed today successfully.
# [CheckCompletion] Completion file: ~/.mxx/completion/2025-12-06.json
# [CheckCompletion] Skipping execution.
# Exits immediately

# If profile failed (processes terminated early):
mxx run up myprofile --var by-completion --kill
# [CheckCompletion] Profile 'myprofile' not yet completed today.
# ... profile runs but processes fail ...
# [Error] Profile processes failed 10 times. Terminating.
# [CheckCompletion] Marked 'myprofile' as failed for today.

# Next run same day (after failure):
mxx run up myprofile --var by-completion
# [CheckCompletion] Profile 'myprofile' not yet completed today.
# ... runs again because previous run failed ...

# Skip even failed runs:
mxx run up myprofile --var by-completion --var include-failed
# [CheckCompletion] Profile 'myprofile' already completed today with failure.
# [CheckCompletion] Skipping execution.
# Exits immediately
```

### Reset Completion Status
```bash
# Reset and run without tracking
mxx run up myprofile --var reset-completion

# Reset and start fresh tracking
mxx run up myprofile --var reset-completion --var by-completion
```

### Include Failed Runs in Skip Check
```bash
# By default, only successful runs prevent re-execution
mxx run up myprofile --var by-completion
# Skips only if previous run was successful (status = true)

# Skip even if previous run failed
mxx run up myprofile --var by-completion --var include-failed
# Skips if ANY run exists today (status = true or false)
```

## How It Works

1. **Activation**: Plugin only activates when `--var by-completion` is passed
2. **Reset handling**: If `--var reset-completion` passed, removes profile from completion file
3. **Pre-check**: Before profile starts, checks `~/.mxx/completion/{today}.json`
   - By default: Only skips if status is `true` (successful)
   - With `--var include-failed`: Skips if any status exists (true or false)
4. **Early exit**: If completion check passes, exits with status 0
5. **Recording**: After profile run, records status to completion file:
   - `true` if profile completed successfully
   - `false` if profile processes failed during execution

## Completion File Format

```json
{
  "myprofile": true,
  "another-profile": false,
  "third-profile": true
}
```

- `true` = Successfully completed
- `false` = Failed during execution
- Files are organized by date: `~/.mxx/completion/2025-12-06.json`

## Available Flags

| Flag | Type | Description |
|------|------|-------------|
| `by-completion` | Boolean | Enable completion tracking and skip check |
| `reset-completion` | Boolean | Reset completion status before running |
| `include-failed` | Boolean | Include failed runs when checking for completion |

## Use Cases

### Scheduled Daily Tasks
```bash
# In cron or task scheduler
0 9 * * * mxx run up daily-backup --var by-completion
```

If the job runs multiple times accidentally, it will only execute once per day (if successful).

### Auto-Retry Failed Runs
```bash
# Retry every hour until successful
0 * * * * mxx run up important-task --var by-completion
```

Failed runs (status=false) won't prevent retries. Only successful runs (status=true) will skip execution.

### Preventing Any Re-runs (Including Failed)
```bash
# Run once per day regardless of success/failure
mxx run up one-time-task --var by-completion --var include-failed
```

### Resetting Completions

Delete the completion file to allow re-running:
```bash
rm ~/.mxx/completion/$(date +%Y-%m-%d).json
```

Or edit the file to remove specific profiles.

## Directory Structure

```
~/.mxx/
└── completion/
    ├── 2025-12-05.json
    ├── 2025-12-06.json
    └── 2025-12-07.json
```

Old completion files can be safely deleted - they're only checked for the current date.

## Integration with Other Plugins

This plugin works alongside other plugins:
- **check-single-instance**: Prevents multiple MXX processes
- **check-free**: Prevents runs during busy periods
- **check-completion**: Prevents duplicate daily runs

All three can be used together for robust run control.
