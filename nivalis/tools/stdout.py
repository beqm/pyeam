import sys
import click

def info(msg: str, exit: bool = False):
    click.echo(f"\033[36;2m[nivalis] \033[0m{msg}")

    if exit:
        sys.exit(0)

def error(msg: str, exit: bool = False):
    click.echo(f"\033[36;2m[nivalis] \033[31m{msg}\033[0m")

    if exit:
        sys.exit(1)