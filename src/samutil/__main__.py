import sys
from os import path

import click
from click.types import Path

from formatting import Formatter
from testing import _test_dir as test_dir
from testing import _test_file as test_file
from testing import _test_non_test_file as test_non_test_file

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
            elif path.isfile(filename):
                if filename.endswith(".test.py"):
                    test_file(filename)
                elif filename.endswith(".py"):
                    test_non_test_file(filename)
            else:
                click.echo(f.info("Skipping", str(file), "as it is not a directory or valid test file."))

if __name__ == "__main__":
    main()