from pathlib import Path
from codecs import open
from setuptools import setup, find_packages

# we're using a README.md, if you do not have this in your folder, simply
# replace this with a string.
here = Path(__file__).parent.resolve()
with open(here / 'README.md', encoding='utf-8') as f:
    long_description = f.read()

# Here you specify the meta-data of your package. The `name` argument is
# needed in some other steps.
setup(
    name='v6-diagnostics',
    version="0.1.0",
    description='vantage6 node diagnostic tools',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vantage6/v6-diagnostics',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'vantage6-client==4.0.0a5',
        'vantage6-algorithm-tools==4.0.0a5',
        'requests',
        'pyjwt',
        'rich',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'vtest=cli.test:cli_test',
        ],
    },
)
