
import click

@click.group()
def action():
    """Run related commands"""
    pass

# run
@action.command("run")
@click.argument("profile")
def run_action(profile):
    """Run auto task for a specific profile"""
    from mxx.auto_profile.mgr import auto_profiles
    
    if profile not in auto_profiles.profiles:
        click.echo(f"profile '{profile}' not found in configuration.")
        return

    profile_obj = auto_profiles.profiles[profile]
    profile_obj.start()
    click.echo(f"profile '{profile}' executed.")

@action.command("kill")
@click.argument("profile")
def kill_action(profile):
    """Kill auto task for a specific profile"""
    from mxx.auto_profile.mgr import auto_profiles
    
    if profile not in auto_profiles.profiles:
        click.echo(f"profile '{profile}' not found in configuration.")
        return

    profile_obj = auto_profiles.profiles[profile]
    profile_obj.kill()
    click.echo(f"profile '{profile}' killed.")
    
@action.command()
@click.option("--sort", "-s", help="sort by a profile value (supports model_extra keys)")
@click.option("--filter", "-f", help="filter by a profile value (by x=y)", multiple=True)
@click.option("--grace", "-g", help="grace period between tasks in seconds", type=int, default=60)
def run(sort, filter, grace):
    """Schedule auto tasks"""
    from mxx.auto_profile.mgr import auto_profiles
    
    # Get list of profiles
    profiles = list(auto_profiles.profiles.items())
    
    # Filter profiles that match the filter criteria
    for f in filter:
        if "=" not in f:
            click.echo(f"Invalid filter format: {f}. Expected format: key=value")
            return
        
        key, value = f.split("=", 1)
        
        # Try to convert value to appropriate type
        def convert_value(v):
            # Try int
            try:
                return int(v)
            except ValueError:
                pass
            # Try bool
            if v.lower() in ("true", "false"):
                return v.lower() == "true"
            # Return as string
            return v
        
        converted_value = convert_value(value)
        
        # Filter by checking regular attributes and model_extra
        filtered = []
        for name, profile in profiles:
            # Check regular attributes
            if hasattr(profile, key):
                if getattr(profile, key) == converted_value:
                    filtered.append((name, profile))
            # Check model_extra for additional fields
            elif key in profile.model_extra:
                if profile.model_extra[key] == converted_value:
                    filtered.append((name, profile))
        
        profiles = filtered
    
    # Sort if requested
    if sort:
        # Sort by the value - check both attributes and model_extra
        def get_sort_key(item):
            name, profile = item
            # Try regular attribute first
            if hasattr(profile, sort):
                return getattr(profile, sort)
            # Try model_extra
            elif sort in profile.model_extra:
                return profile.model_extra[sort]
            # Return empty string if not found
            return ""
        
        profiles.sort(key=get_sort_key)
    
    # Display results
    if not profiles:
        click.echo("No profiles match the criteria.")
        return
    
    # Collect all unique keys from model_extra across all profiles
    extra_keys = set()
    for _, profile in profiles:
        if profile.model_extra:
            extra_keys.update(profile.model_extra.keys())
    extra_keys = sorted(extra_keys)
    
    # Build table headers
    headers = ["Name", "MAA", "LD", "Wait", "Lifetime"] + extra_keys
    
    # Build table rows
    rows = []
    for name, profile in profiles:
        row = [
            name,
            profile.maa,
            str(profile.ld) if profile.ld is not None else "-",
            str(profile.waitTime),
            str(profile.lifetime)
        ]
        
        # Add model_extra values
        for key in extra_keys:
            value = profile.model_extra.get(key, "-") if profile.model_extra else "-"
            row.append(str(value))
        
        rows.append(row)
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    
    # Print table
    click.echo(f"\nFound {len(profiles)} profile(s):\n")
    
    # Print header
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    click.echo(header_line)
    click.echo("-" * len(header_line))
    
    # Print rows
    for row in rows:
        row_line = " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
        click.echo(row_line)
