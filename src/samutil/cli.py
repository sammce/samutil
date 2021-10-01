from os import path

import click
from click.types import Path

from formatting import Formatter
from testing.utils import test_dir, test_file, test_test_file

f = Formatter()

@click.group()
@click.version_option("0.0.62")
def main():
    """Samutil Python CLI"""
    pass


@main.command()
@click.argument('filenames', type=click.Path(exists=True), nargs=-1, required=False)
def test(filenames: tuple[Path]):
    if len(filenames) == 0:
        test_dir(".")
    else:
        for file in filenames:
            filename = click.format_filename(file)

            if path.isdir(filename):
                test_dir(filename)
            elif path.isfile(filename) and filename.endswith(".py"):
                if filename.endswith(".test.py"):
                    test_test_file(filename)
                else:
                    test_file(filename)
            else:
                click.echo(f.info("Skipping", str(file), "as it is not a directory or valid test file."))

if __name__ == "__main__":
    main()
