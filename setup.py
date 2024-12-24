from setuptools import setup, find_packages

setup(
    name="fvs-python",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'scipy>=1.7.0',
    ],
    author="Chris Mihiar",
    author_email="chris.mihiar@gmail.com",
    description="Python implementation of the Southern variant of the Forest Vegetation Simulator",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mihiarc/fvs-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
)