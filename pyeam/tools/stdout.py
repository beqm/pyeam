import click

def info(msg: str):
    click.echo(f"\033[36;2m[pyeam] \033[0m{msg}")

def error(msg: str):
    click.echo(f"\033[36;2m[pyeam] \033[31m{msg}\033[0m")