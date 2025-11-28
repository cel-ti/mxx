import os
import click
from mxx.app.mgr import mxxmgr
from mxx.maaconfig.mgr import mxxmaa
from mxx.auto_profile.mgr import auto_profiles

@click.group()
def app():
    """app related commands"""
    pass

@app.group("config")
def config():
    """Set path configurations"""
    pass

@config.command("profile-path")
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def set_profile_path(path):
    """Set the profile path"""
    mxxmgr.config.profile_path = path
    mxxmgr.save_config()
    click.echo(f"Profile path set to: {path}")

@config.command("maaconfig-path")
@click.argument("path", type=click.Path(exists=True, file_okay=True, dir_okay=False))
def set_maaconfig_path(path):
    """Set the MAA config path"""
    mxxmgr.config.maaconfig_path = path
    mxxmgr.save_config()
    click.echo(f"MAA config path set to: {path}")

@config.command("maa-backup")
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def set_maaconfig_backup_path(path):
    """Set the MAA config backup path"""
    mxxmgr.config.maaconfig_bkup_path = path
    mxxmgr.save_config()
    click.echo(f"MAA config backup path set to: {path}")

@config.command("show")
def show_config():
    """Show current configuration"""
    click.echo(f"Profile Path: {auto_profiles.configDir}")
    click.echo(f"MAA Config Path: {mxxmaa.configDir}")
    click.echo(f"MAA Config Backup Path: {mxxmaa.bkupDir}")


@config.command("clear")
def clear_config():
    """Clear all configurations"""
    mxxmgr.config.profile_path = None
    mxxmgr.config.maaconfig_path = None
    mxxmgr.config.maaconfig_bkup_path = None
    mxxmgr.save_config()
    click.echo("All configurations cleared.")

@config.command("open")
def open_config():
    os.startfile(os.path.dirname(mxxmgr.configPath))