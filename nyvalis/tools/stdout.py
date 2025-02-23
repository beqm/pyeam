import sys
import click
from nyvalis.core import LIB_NAME

def info(msg: str, exit: bool = False):
    click.echo(f"\033[36;2m[{LIB_NAME}] \033[0m{msg}")

    if exit:
        sys.exit(0)

def error(msg: str, exit: bool = False):
    click.echo(f"\033[36;2m[{LIB_NAME}] \033[31m{msg}\033[0m")

    if exit:
        sys.exit(1)