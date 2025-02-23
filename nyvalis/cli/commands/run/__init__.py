import os
import sys
import click
import subprocess
from nyvalis.tools import stdout, log
from nyvalis.core import CONF_FILENAME

logger = log.get(log.LIB_NAME)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help="Change lib logger level to DEBUG")
def run(verbose):
    """Runs the project for development
    """

    run_application(verbose)

    os.chdir("src-python")

    run_application(verbose)


def run_application(verbose: bool):
    if os.path.isfile("main.py"):
        if os.path.isfile(CONF_FILENAME):
            try:
                if verbose:
                    subprocess.run([sys.executable, "main.py", "-v"], check=True)
                else:
                    subprocess.run([sys.executable, "main.py"], check=True)
            except subprocess.CalledProcessError:
                stdout.error("Failed to run application")
                return
        else:
            stdout.error(f"Could not find application.")