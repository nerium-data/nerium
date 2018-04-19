from setuptools import setup, find_packages

setup(
    name='nerium',
    version='0.1.0',
    packages=find_packages(),
    description='The little database engine that could',
    author='Thomas Yager-Madden',
    author_email='thomas.yager-madden@adops.com',
    install_requires=[
        'Flask',
        'Flask-RESTful',
        'python-dotenv',
        'records',
    ],
    extras_require={
        'mysql': ['PyMySQL'],
        'pg': ['psycopg2'],
        # TODO: Add the rest.
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        ],
    url='https://github.com/OAODEV/nerium',
)
