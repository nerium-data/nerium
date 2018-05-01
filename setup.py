from setuptools import setup, find_packages

setup(
    name='nerium',
    version='0.1.0',
    packages=find_packages(),
    description='The little business intelligence engine that could',
    author='Thomas Yager-Madden',
    author_email='thomas.yager-madden@adops.com',
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
    include_package_data=True,
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
