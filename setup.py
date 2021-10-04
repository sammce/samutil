from setuptools import find_packages, setup

# # The directory containing this file
# HERE = pathlib.Path(__file__).parent
# # The text of the README file
# README = (HERE / "README.md").read_text()
# # automatically captured required modules for install_requires in requirements.txt and as well as configure dependency links
# with open(path.join(HERE, "requirements.txt"), encoding="utf-8") as f:
#     all_reqs = f.read().split("\n")
# install_requires = [
#     x.strip()
#     for x in all_reqs
#     if ("git+" not in x) and (not x.startswith("#")) and (not x.startswith("-"))
# ]
# dependency_links = [x.strip().replace("git+", "") for x in all_reqs if "git+" not in x]

setup(
    name="samutil",
    description="A set of Python utility packages for developing and maintaining quality software.",
    version="0.0.70",
    packages=find_packages(where="samutil"),
    package_dir={"": "samutil"},
    install_requires=["click", "sigfig", "sortedcontainers"],
    python_requires=">=3",
    entry_points="""
        [console_scripts]
        samutil=samutil.__cli__:main
    """,
    author="Sam McElligott",
    keyword="testing, unittesting, formatting, secure, generation, utility",
    long_description="README.md",
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/sammce/samutil",
    project_urls={
        "Bug Tracker": "https://github.com/sammce/samutil/issues",
    },
    author_email="sammcelligott@outlook.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)
