import os
import click
import questionary
from nivalis.tools import stdout
from nivalis.cli.commands import utils
from nivalis.cli.commands.models import PackageManager, PackageManagerEnum, TemplateObj, BuildField

FULL_PATH = None

class TemplateEnum:
    from nivalis.cli.commands.new.svelte import create_svelte_app
    from nivalis.cli.commands.new.react import create_react_app
    
    SVELTE = TemplateObj(title="Svelte", value="SVELTE", create=create_svelte_app, 
                        build_field=BuildField("http://localhost:5173", "dist", r"{{ manager }} dev", r"{{ manager }} build"))
    
    REACT = TemplateObj(title="React", value="REACT", create=create_react_app, 
                        build_field=BuildField("http://localhost:5173", "dist", r"{{ manager }} dev", r"{{ manager }} build"))

@click.command()
@click.argument("name", required=False)
def new(name: str = None):
    """Creates a new project

    name: The name of the project. If not provided, you will be asked to enter one.
    """

    global FULL_PATH
    
    if not name:
        name = utils.prompt_text("Project name", default=".")

    FULL_PATH = os.path.join(os.getcwd(), name)

    if os.path.exists(FULL_PATH):
        if os.listdir(FULL_PATH):
            stop = utils.prompt_select(title="Directory not empty, continue?", choices=[questionary.Choice(title="Yes", value=False),
                questionary.Choice(title="No", value=True)])
            
            if stop:
                stdout.error("Operation cancelled by user.", exit=True)

    manager: PackageManager = utils.prompt_select(title="Choose the package manager", choices=[questionary.Choice(title="npm", value=PackageManagerEnum.NPM),
        questionary.Choice(title="pnpm", value=PackageManagerEnum.PNPM)])

    scaffold_template(manager, name)

    if not os.path.exists(os.path.join(FULL_PATH, ".venv")):
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


def scaffold_template(manager: PackageManager, path: str):
    template: TemplateObj = utils.prompt_select(title="Choose your desired UI framework", choices = [
                                questionary.Choice(title=tc.title, value=tc) 
                                for tc in TemplateEnum.__dict__.values() 
                                if isinstance(tc, TemplateObj)
                            ]) 

    if not utils.is_cli_installed("npm"):
        stdout.error("NPM is not installed. Install at https://nodejs.org/en", exit=True)

    template.create(path)

    if not os.path.exists(os.path.join(FULL_PATH, ".git")):
        create_repo = utils.prompt_select(
            title=f"Create git repository?",
            choices=[
                questionary.Choice(title="Yes", value=True),
                questionary.Choice(title="No", value=False)
            ]
        )

        if create_repo:
            if utils.is_cli_installed("npm"):
                utils.create_git_repo(FULL_PATH)
            else:
                stdout.error("Git is not installed. Install at https://git-scm.com/", exit=True)

    utils.write_requirements(path)
    utils.scaffold_python(manager, path, template)
