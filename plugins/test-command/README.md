# MXX Test Command Plugin

A test plugin that demonstrates how to add CLI commands to MXX.

## Features

- Adds a `test` command to the MXX CLI
- Demonstrates command registration via `register_commands()`
- Shows pre/post command hooks in action

## Installation

```bash
cd plugins/test-command
uv pip install -e .
```

## Usage

```bash
mxx test
mxx test --name Alice
```

## Hooks Demonstrated

- `register_commands(cli_group)` - Registers the test command
- `hook_pre_command(command_name, ctx)` - Runs before test command
- `hook_post_command(command_name, ctx, result)` - Runs after test command
