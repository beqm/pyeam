import os
import sys
import click
import questionary
from pyeam.tools import stdout
from pyeam.cli.commands import utils
from pyeam.cli.config import TemplateEnum, PackageManager, PackageManagerEnum

@click.command()
@click.argument("name", required=False)
def new(name: str = None):
    """Starts the new application prompt

    name: The name of the project. If not provided, you will be asked to enter one.
    """

    try:
        if not name:
            name = utils.prompt_text("Project name", default=".")

        manager = utils.prompt_select(title="Choose the package manager", choices=[questionary.Choice(title="npm", value=PackageManagerEnum.NPM),
            questionary.Choice(title="pnpm", value=PackageManagerEnum.PNPM)])

        scaffold_template(manager, name)

        venv = utils.prompt_select(title="Would you like to set up venv?", choices=[questionary.Choice(title="Yes", value=True),
            questionary.Choice(title="No", value=False)])
        
        pip = utils.prompt_select(title="Would you like to run pip install?", choices=[questionary.Choice(title="Yes", value=True),
            questionary.Choice(title="No", value=False)])

        if venv:
            utils.setup_venv(name)

        if pip:
            utils.run_pip_install(name, venv)

        if not os.path.exists(os.path.join(name, "node_modules")):
            npm = utils.prompt_select(title="Would you like to run npm install?", choices=[questionary.Choice(title="Yes", value=True),
                questionary.Choice(title="No", value=False)])
        
            if npm:
                utils.run_npm_install(name, manager)

        stdout.info("Project setup completed successfully!")
    except KeyboardInterrupt:
        stdout.info("Operation cancelled by user")


def scaffold_template(manager: PackageManager, path: str):
    template = utils.prompt_select(title="Choose your desired UI framework", choices=[questionary.Choice(title="Svelte", value=TemplateEnum.SVELTE),
        questionary.Choice(title="React", value=TemplateEnum.REACT)])

    if not utils.is_npm_installed():
        stdout.error("NPM is not installed. See https://nodejs.org/en")
        sys.exit(1)

    if template == TemplateEnum.SVELTE:
        utils.create_svelte_app(path)
    elif template == TemplateEnum.REACT:
        utils.create_react_app(path)
    else:
        sys.exit(1)

    _, error = utils.write_requirements(path)

    if error:
        stdout.error(f"Failed to write requirements.txt: {error}")

    utils.scaffold_python(manager, path, template)


