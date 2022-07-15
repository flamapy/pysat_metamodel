import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="famapy-sat",
    version="1.0.0",
    author="Víctor Ramírez de la Corte",
    author_email="me@virako.es",
    description="famapy-sat is a plugin to FaMaPy module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FaMaPy/pysat_metamodel",
    packages=setuptools.find_namespace_packages(include=['famapy.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        'famapy~=1.0.0',
        'famapy-fm~=1.0.0',
        'python-sat>=0.1.7.dev6'
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-mock',
            'prospector',
            'mypy',
            'coverage',
        ]
    },
    dependency_links=[
        'famapy~=1.0.0'
    ]
)
