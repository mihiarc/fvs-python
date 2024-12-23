from setuptools import setup, find_packages

setup(
    name='fvs_python',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'pandas'
    ],
    python_requires='>=3.7',
    description='Southern FVS Variant for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Chris Mihiar',
    author_email='chris.mihiar@gmail.com',
    url='https://github.com/mihiarc/fvs-python',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)