# MXX Check Single Instance Plugin

Ensures only one instance of MXX can run at a time.

## Features

- Checks for other running `mxx.exe` processes during plugin initialization
- Exits early with error message if another instance is detected
- Uses `psutil` to enumerate running processes

## Installation

From the plugin directory:

```bash
uv pip install -e .
```

## Usage

This plugin automatically activates when MXX starts. If another instance is detected, the application will exit with:

```
CheckSingleInstance: Found 1 other MXX instance(s) running.
CheckSingleInstance: Only one instance of MXX is allowed. Exiting...
```

## How It Works

The plugin implements the `init()` hook from `PluginInterface`:
1. Gets the current process PID
2. Iterates through all running processes looking for `mxx.exe`
3. Filters out the current process
4. If any other instances exist, calls `sys.exit(1)` to terminate early

## Dependencies

- `psutil>=5.9.0` - For process enumeration
