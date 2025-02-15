import os
import sys
import click
import subprocess
from nivalis.tools import stdout


@click.command()
def run():
    
    run_application()

    os.chdir("src-python")

    run_application()


def run_application():
    if os.path.isfile("main.py"):
        if os.path.isfile("nivalis.conf.json"):
            try:
                subprocess.run([sys.executable, "main.py"], check=True)
            except subprocess.CalledProcessError:
                stdout.error("Failed to run application")
                return
        else:
            stdout.error(f"Could not find application.")