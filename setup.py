from setuptools import setup, find_packages

from pathlib import Path


with open(Path(__file__).parent / 'README.md') as f:
    long_description = f.read()

setup(
    name='nerium',
    version='0.1.2',
    packages=find_packages(),
    description='The little business intelligence engine that could',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Thomas Yager-Madden',
    author_email='thomas.yager-madden@adops.com',
    license='Apache License, Version 2.0',
    install_requires=[
        'aiohttp',
        'python-dotenv',
        'records',
    ],
    extras_require={
        'mysql': ['PyMySQL'],
        'pg': ['psycopg2'],
        # TODO: Add the rest.
    },
    # TODO: A more sophisticated runserver CLI
    entry_points={
        'console_scripts': [
            'nerium = nerium.app:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: AsyncIO',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    url='https://github.com/OAODEV/nerium',
)
