import os
import sys
import click
import logging
import subprocess
from pyeam.tools import stdout


@click.command()
def run(counter=0):

    MAX_RECURSION = 2

    if counter >= MAX_RECURSION:
        return
    
    if os.path.isfile("main.py"):
        if os.path.isfile("pyeam.conf.json"):
            try:
                subprocess.run([sys.executable, "main.py"], check=True)
            except subprocess.CalledProcessError:
                return
        else:
            stdout.error(f"Could not find application.")
    else:
        if os.path.isdir("src-pyeam"):
            os.chdir("src-pyeam")
            run(counter + 1)
        else:
            stdout.error(f"Could not find application.")