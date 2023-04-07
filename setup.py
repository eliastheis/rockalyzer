from setuptools import setup


# read the contents of your README file for the long description
with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='rockalyzer',
    version='0.0.2',
    description='Rocket League Analyzer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/eliastheis/rockalyzer',
    author='Elias Theis',
    author_email='mail@eliastheis.de',
    py_modules=['rockalyzer', 'Game', 'Action', 'console_colors', 'constants'],
    package_dir={'': 'src'},
    install_requires=[
        'numpy',
        'matplotlib',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

)
