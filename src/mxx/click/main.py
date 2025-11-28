
import click

from mxx.click.app import app
from mxx.click.maa import maa
from mxx.click.auto import auto
from mxx.click.action import action
from mxx.plugin_system.loader import mxx_plugin_loader

from mxx.maaconfig.mgr import mxxmaa
from mxx.auto_profile.mgr import auto_profiles

mxxmaa.profiles.update(mxx_plugin_loader.loadMaaProfiles())
auto_profiles.profiles.update(mxx_plugin_loader.loadProfiles())


@click.group()
def cli():
    """MXX Application Command Line Interface"""
    pass


cli.add_command(app)
cli.add_command(maa)
cli.add_command(auto)
cli.add_command(action)