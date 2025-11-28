import click


@click.group()
def auto():
    """Auto profile management commands"""
    pass


@auto.command("list")
def list_profiles():
    """List all auto profiles"""
    from mxx.auto_profile.mgr import auto_profiles
    
    if not auto_profiles.profiles:
        click.echo("No auto profiles configured.")
        return

    click.echo("Configured auto profiles:")
    for profile_name in auto_profiles.profiles:
        click.echo(f" - {profile_name}")


@auto.command("info")
@click.argument("profile")
def info_profile(profile):
    """Show information about a specific auto profile"""
    from mxx.auto_profile.mgr import auto_profiles
    from pprint import pformat
    
    if profile not in auto_profiles.profiles:
        click.echo(f"Auto profile '{profile}' not found in configuration.")
        return

    profile_obj = auto_profiles.profiles[profile]
    click.echo(pformat(profile_obj.model_dump()))


@auto.command("open")
@click.option("--profile", "-p", help="Auto profile name")
def open_profile(profile):
    """Open auto profile configuration file or folder"""
    from mxx.auto_profile.mgr import auto_profiles
    from mxx.utils.resolveEditor import resolve_editor
    import os

    if profile:
        # Open the profile TOML file directly
        profile_file = auto_profiles.configDir / f"{profile}.toml"
        
        if not profile_file.exists():
            click.echo(f"Auto profile '{profile}' configuration file not found at {profile_file}")
            return
        
        resolve_editor(profile_file)
        click.echo(f"Opening {profile_file}")
    else:
        os.startfile(auto_profiles.configDir)


@auto.command("new")
@click.argument("profile")
@click.option("--maa", "-m", help="MAA app name", default="default")
@click.option("--ld", type=int, help="LD player index")
def new_profile(profile, maa, ld):
    """Create a new auto profile"""
    from mxx.auto_profile.mgr import auto_profiles
    from mxx.utils.toml import save_toml
    from mxx.auto_profile.model import MxxAutoProfile

    if profile in auto_profiles.profiles:
        click.echo(f"Auto profile '{profile}' already exists in configuration.")
        return

    # Create a new MxxAutoProfile
    profile_data = {"maa": maa}
    if ld is not None:
        profile_data["ld"] = ld
    
    profile_obj = MxxAutoProfile(**profile_data)
    
    # Save to TOML file
    profile_path = auto_profiles.configDir / f"{profile}.toml"
    save_toml(profile_obj.model_dump(), str(profile_path))
    
    # Reload profiles
    auto_profiles.profiles[profile] = profile_obj
    
    click.echo(f"Created auto profile '{profile}' at {profile_path}")

@auto.command("run")
@click.argument("profile")
def run_profile(profile):
    """Run an auto profile"""
    from mxx.auto_profile.mgr import auto_profiles

    auto_profiles.profiles[profile].start()


