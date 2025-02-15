import os
import click
import questionary
from nivalis.tools import stdout
from nivalis.cli.commands import utils
from nivalis.cli.commands.models import PackageManager, PackageManagerEnum, TemplateObj, TemplateEnum


@click.command()
@click.argument("name", required=False)
def new(name: str = None):
    """Starts the new application prompt

    name: The name of the project. If not provided, you will be asked to enter one.
    """

    try:
        if not name:
            name = utils.prompt_text("Project name", default=".")

        full_path = os.path.join(os.getcwd(), name)

        if os.path.exists(full_path):
            if os.listdir(full_path):
                stop = utils.prompt_select(title="Directory not empty, continue?", choices=[questionary.Choice(title="Yes", value=False),
                    questionary.Choice(title="No", value=True)])
                
                if stop:
                    stdout.error("Operation cancelled by user.", exit=True)

        manager: PackageManager = utils.prompt_select(title="Choose the package manager", choices=[questionary.Choice(title="npm", value=PackageManagerEnum.NPM),
            questionary.Choice(title="pnpm", value=PackageManagerEnum.PNPM)])

        template_choice(manager, name)


        if not os.path.exists(os.path.join(full_path, ".venv")):
            venv: bool = utils.prompt_select(title="Would you like to set up venv?", choices=[questionary.Choice(title="Yes", value=True),
                questionary.Choice(title="No", value=False)])
            
            if venv:
                utils.setup_venv(name)
        
        pip: bool = utils.prompt_select(title="Would you like to run pip install?", choices=[questionary.Choice(title="Yes", value=True),
            questionary.Choice(title="No", value=False)])


        if pip:
            utils.run_pip_install(name, venv)

        if not os.path.exists(os.path.join(name, "node_modules")):
            node_modules = utils.prompt_select(title=f"Would you like to run {manager.cli} install?", choices=[questionary.Choice(title="Yes", value=True),
                questionary.Choice(title="No", value=False)])
        
            if node_modules:
                utils.run_npm_install(name, manager)

        stdout.info("Project setup completed successfully!")
    except KeyboardInterrupt:
        stdout.info("Operation cancelled by user")

def template_choice(manager: PackageManager, path: str):
    template: TemplateObj = utils.prompt_select(title="Choose your desired UI framework", choices = [
                                questionary.Choice(title=tc.title, value=tc) 
                                for tc in TemplateEnum.__dict__.values() 
                                if isinstance(tc, TemplateObj)
                            ]) 

    if not utils.is_npm_installed():
        stdout.error("NPM is not installed. See https://nodejs.org/en", exit=True)

    template.func(path)

    utils.write_requirements(path)
    utils.scaffold_python(manager, path, template.value)
