import click
from nivalis.cli.commands import run, new

@click.group()
def main():
    pass

main.add_command(new, name="new")
main.add_command(run, name="run")


if __name__ == "__main__":
    main()