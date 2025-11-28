
import datetime
from pprint import pformat
import click

@click.group()
def maa():
    """maa framework commands"""
    pass

@maa.command("backup")
@click.argument("maa")
@click.option("--output", "-o", type=click.Path(), help="Output backup zip file path")
def backup_maa(maa, output):
    """Backup MAA app data to a zip file"""
    from mxx.maaconfig.mgr import mxxmaa
    if maa not in mxxmaa.profiles:
        click.echo(f"MAA app '{maa}' not found in configuration.")
        return

    if output is None:
        output = mxxmaa.bkupDir / f"{maa}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.zip"

    mxxmaa.profiles[maa].backup(output)
    click.echo(f"MAA app '{maa}' backed up to '{output}'")

@maa.command("restore")
@click.argument("maa")
@click.option("--input", "-i", type=click.Path(exists=True), help="Input backup zip file path", required=True)
@click.option("--latest", "-l", is_flag=True, help="Use latest backup file")
def restore_maa(maa, input, latest):
    """Restore MAA app data from a zip file"""
    from mxx.maaconfig.mgr import mxxmaa
    import glob
    import os

    if maa not in mxxmaa.profiles:
        click.echo(f"MAA app '{maa}' not found in configuration.")
        return

    if latest:
        bkup_files = sorted(
            glob.glob(os.path.join(mxxmaa.bkupDir, f"{maa}_*.zip")),
            key=os.path.getmtime,
            reverse=True
        )
        if not bkup_files:
            click.echo(f"No backup files found for MAA app '{maa}'.")
            return
        input = bkup_files[0]

    mxxmaa.profiles[maa].restore(input)
    click.echo(f"MAA app '{maa}' restored from '{input}'")

@maa.command("list")
def list_maas():
    """List all configured MAA apps"""
    from mxx.maaconfig.mgr import mxxmaa
    if not mxxmaa.profiles:
        click.echo("No MAA apps configured.")
        return

    click.echo("Configured MAA apps:")
    for maa_name in mxxmaa.profiles:
        click.echo(f" - {maa_name}")

@maa.command("info")
@click.argument("maa")
def info_maa(maa):
    """Show information about a specific MAA app"""
    from mxx.maaconfig.mgr import mxxmaa
    if maa not in mxxmaa.profiles:
        click.echo(f"MAA app '{maa}' not found in configuration.")
        return

    profile = mxxmaa.profiles[maa]

    #print json
    click.echo(pformat(profile.config.model_dump()))

@maa.command("open")
@click.option("--maa", "-m", help="MAA app name")
@click.option("--backup", "-b", is_flag=True, help="Open mxx backup directory")
def open_maa(maa, backup):
    """Open MAA app configuration directory or file"""
    from mxx.maaconfig.mgr import mxxmaa
    from mxx.utils.resolveEditor import resolve_editor
    import os

    if maa:
        # Open the profile TOML file directly without validation
        profile_file = mxxmaa.configDir / f"{maa}.toml"
        
        if not profile_file.exists():
            click.echo(f"MAA app '{maa}' configuration file not found at {profile_file}")
            return
        
        resolve_editor(profile_file)
        click.echo(f"Opening {profile_file}")
    elif backup:
        os.startfile(mxxmaa.bkupDir)
    else:
        os.startfile(mxxmaa.configDir)

@maa.command("new", help="Create a new MAA app configuration")
@click.argument("maa")
def new_maa(maa):
    """Create a new MAA app configuration"""
    from mxx.maaconfig.mgr import mxxmaa
    from mxx.utils.toml import save_toml

    if maa in mxxmaa.profiles:
        click.echo(f"MAA app '{maa}' already exists in configuration.")
        return

    # Create a new MaaProfile with default values
    from mxx.maaconfig.model import MaaProfile, MaaConfig
    
    profile = MaaProfile(
        path="",
        configFolder="config",
        config=MaaConfig(),
        app=""
    )
    
    # Save to TOML file
    profile_path = mxxmaa.configDir / f"{maa}.toml"
    save_toml(profile.model_dump(), str(profile_path))
    
    # Reload profiles
    mxxmaa.profiles[maa] = profile
    
    click.echo(f"Created MAA app configuration '{maa}' at {profile_path}")
    