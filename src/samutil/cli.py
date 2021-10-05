from os import getcwd, path

import click

from .formatting import Formatter as f
from .generation.core import generate_key
from .testing.utils import test_dir, test_file, test_test_file


@click.group("samutil")
@click.version_option("0.0.71")
def main():
    """Samutil Python CLI"""
    pass


@main.command("test")
@click.argument("filenames", nargs=-1, required=False)
def test(filenames: tuple[click.Path]):
    if len(filenames) == 0:
        test_dir(getcwd(), search=True)
    else:
        if filenames[0] == ".":
            print(f.error("To test an entire directory, use '*'"))
            return
        for file in filenames:
            filename = click.format_filename(file)
            ignore_dirs = ["__pycache__", "venv", "env", "virtualenv", "build", "dist"]
            if path.isdir(filename):
                if filename not in ignore_dirs:
                    test_dir(filename, search=False)
            elif path.isfile(filename) and filename.endswith(".py"):
                if filename.endswith(".test.py"):
                    test_test_file(filename)
                else:
                    test_file(filename, search=False)
            else:
                print(
                    f.warning(
                        "WARNING: Skipping",
                        f.underline(f.bold(str(file))),
                        "as it is not a directory or valid test file.",
                    )
                )


@main.command("key")
@click.option("-l", "--length", type=int, default=6)
@click.option("-a", "--amount", type=int, default=1)
@click.option("-o", "--out", type=str, default=None)
def key(length: int = 6, amount: int = 1, out: click.Path = None):
    tokens = []
    for _ in range(amount):
        tokens.append(generate_key(length))

    if out:
        with open(out, "w+") as o:
            o.write("\n".join(tokens))
            print(f.success("Wrote tokens to", f.bold(out)))
    else:
        print("\n" + "\n".join(tokens) + "\n")


if __name__ == "__main__":
    main()
