# -*- coding: utf-8 -*-

"""Top-level package for giface"""

import click
import confuse
import pprint

from giface import commands

__author__ = """J0J0"""
__version__ = '0.1.0'


@click.group()
def cli():
    pass


# Add commands
cli.add_command(commands.auto)
