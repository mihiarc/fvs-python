from setuptools import setup, find_packages

setup(
    name="fvs-python",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'pytest'
    ],
)