from os import getcwd, path

import click

from formatting import Formatter as f
from generation.core import generate_key
from testing.utils import test_dir, test_file, test_test_file


@click.group()
@click.version_option("0.0.69")
def main():
    """Samutil Python CLI"""
    pass


@main.command()
@click.argument("filenames", type=click.Path(exists=True), nargs=-1, required=False)
@click.pass_context
def test(ctx: click.Context, filenames: tuple[click.Path]):

    if len(filenames) == 0:
        test_dir("./", search=True)
    else:
        for file in filenames:
            filename = click.format_filename(file)

            if path.isdir(filename):
                test_dir(filename, search=False)
            elif path.isfile(filename) and filename.endswith(".py"):
                if filename.endswith(".test.py"):
                    test_test_file(filename)
                else:
                    test_file(filename, search=False)
            else:
                click.echo(
                    f.info(
                        "Skipping",
                        str(file),
                        "as it is not a directory or valid test file.",
                    )
                )


@main.command()
@click.option("-l", "--length", type=int, default=6)
@click.option("-a", "--amount", type=int, default=1)
@click.option("-o", "--out", type=click.Path("w+"), default=None)
def key(length: int = 6, amount: int = 1, out: click.Path = None):
    tokens = []
    for _ in range(amount):
        tokens.append(generate_key(length))

    if out:
        out.write("\n".join(tokens))
        print(f.success("Wrote tokens to", f.bold(out)))
    else:
        print("\n" + "\n".join(tokens) + "\n")


if __name__ == "__main__":
    main()
