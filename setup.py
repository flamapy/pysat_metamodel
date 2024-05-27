import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="flamapy-sat",
    version="2.0.0.dev1",
    author="Flamapy",
    author_email="flamapy@us.es",
    description="flamapy-sat is a plugin to flamapy module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flamapy/pysat_metamodel",
    packages=setuptools.find_namespace_packages(include=['flamapy.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        'flamapy-fw~=2.0.0.dev1',
        'flamapy-fm~=2.0.0.dev1',
        'python-sat>=0.1.7.dev1'
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
        'flamapy~=2.0.0.dev1',
    ]
)
