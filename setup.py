from setuptools import find_packages, setup

setup(
    name="samutil",
    description="A set of Python utility packages for developing and maintaining quality software.",
    version="0.0.75",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["click", "sigfig", "sortedcontainers"],
    python_requires=">=3",
    include_package_data=True,
    py_modules=["cli"],
    entry_points="""
        [console_scripts]
        samutil = samutil.cli:main
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
