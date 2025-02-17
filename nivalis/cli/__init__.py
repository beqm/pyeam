import click
from nivalis.cli.commands import run, new, build

@click.group()
def main():
    pass

main.add_command(new, name="new")
main.add_command(run, name="run")
main.add_command(build, name="build")


if __name__ == "__main__":
    main()