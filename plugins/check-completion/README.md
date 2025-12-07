# MXX Check Completion Plugin

Tracks profile completions per day to prevent duplicate runs.

## Features

- **Daily completion tracking** - Uses `~/.mxx/completion/{date}.json` to track completions
- **Opt-in behavior** - Only activates with `--var by-completion`
- **Early exit** - Exits immediately if profile already completed today
- **Automatic recording** - Marks completion after successful profile start
- **Reset capability** - Reset completion status with `--var reset-completion`
- **Boolean flag support** - Use `--var by-completion` (no `=true` needed)

## Installation

```bash
cd plugins/check-completion
pip install .
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

# First run: [CheckCompletion] Profile 'myprofile' not yet completed today.
#            [CheckCompletion] Will track completion after successful run.
#            ... profile runs ...
#            [CheckCompletion] Marked 'myprofile' as completed for today.

# Second run same day:
mxx run up myprofile --var by-completion
# [CheckCompletion] Profile 'myprofile' already completed today.
# [CheckCompletion] Completion file: ~/.mxx/completion/2025-12-06.json
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

## How It Works

1. **Activation**: Plugin only activates when `--var by-completion` is passed
2. **Reset handling**: If `--var reset-completion` passed, removes profile from completion file
3. **Pre-check**: Before profile starts, checks `~/.mxx/completion/{today}.json`
4. **Early exit**: If profile name found in completion file (and by-completion enabled), exits with status 0
5. **Recording**: After successful profile start (and by-completion enabled), records profile name to completion file

## Completion File Format

```json
{
  "myprofile": true,
  "another-profile": true
}
```

Files are organized by date: `~/.mxx/completion/2025-12-06.json`

## Use Cases

### Scheduled Daily Tasks
```bash
# In cron or task scheduler
0 9 * * * mxx run up daily-backup --var by-completion=true
```

If the job runs multiple times accidentally, it will only execute once per day.

### Preventing Accidental Re-runs
```bash
# Safe to run multiple times
mxx run up data-import --var by-completion=true
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
