# MXX Test Command Override Plugin

A test plugin that demonstrates how to extend/override command behavior through hooks.

## Features

- **Does NOT replace** the original `test` command
- **Extends behavior** using pre/post command hooks
- Shows how to access command parameters from context
- Adds a complementary `test-info` command
- Demonstrates error handling hooks

## Installation

```bash
cd plugins/test-command-override
uv pip install -e .
```

## Usage

When both `mxxp-test-command` and `mxxp-test-command-override` are installed:

```bash
mxx test              # Runs with both plugins' hooks
mxx test --name Alice # Parameters accessible in hooks
mxx test-info        # Shows enhancement info
```

## Output Example

```
============================================================
[TestCommandOverridePlugin] ⚡ Enhanced test mode activated!
============================================================
[TestCommandOverridePlugin] Processing for user: Alice
[TestCommandPlugin] Pre-command hook: test command starting...
Hello Alice from TestCommandPlugin!
This is the base test command.
[TestCommandPlugin] Post-command hook: test command completed!
============================================================
[TestCommandOverridePlugin] ✨ Additional features activated:
  - Logging enabled
  - Metrics collected
  - Enhancement layer applied
============================================================
```

## How It Works

This plugin demonstrates the **decorator pattern** for commands:
1. Original command executes normally
2. Multiple plugins can hook into execution
3. Hooks run in plugin load order
4. Each plugin adds its own layer of functionality
5. No plugin needs to know about others

This is more maintainable than having plugins override/replace commands.
