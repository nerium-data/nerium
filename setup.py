from setuptools import setup, find_packages

from pathlib import Path

with open(Path(__file__).parent / 'README.md') as f:
    long_description = f.read()

with open('nerium/version.py') as version:
    exec(version.read())

setup(
    name='nerium',
    version=__version__,  # noqa F821
    packages=find_packages(),
    description='The little business intelligence engine that could',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Thomas Yager-Madden',
    author_email='thomas.yager-madden@adops.com',
    license='Apache License, Version 2.0',
    test_suite='tests',
    install_requires=[
        'munch',
        'python-dotenv',
        'python-frontmatter',
        'pyyaml',
        'records',
        'responder'
    ],
    extras_require={
        'mysql': ['PyMySQL'],
        'pg': ['psycopg2'],
    },
    # TODO: A more sophisticated runserver CLI
    entry_points={'console_scripts': [
        'nerium = nerium.app:main',
    ]},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: AsyncIO',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    url='https://github.com/OAODEV/nerium',
)
