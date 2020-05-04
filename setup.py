"Setuptools configuration"

# stdlib
from os.path import realpath, dirname, join
from setuptools import setup

EXTRA_SETUPS = ('docs',)

if __name__ == '__main__':
    reqs = []
    extras = {}
    abspath = realpath(dirname(__file__))

    with open(join(abspath, 'requirements.txt')) as reqfile:
        reqs = reqfile.readlines()

    for extra in EXTRA_SETUPS:
        filename = 'requirements_{extra}.txt'.format(extra=extra)

        with open(join(abspath, filename)) as reqfile:
            extras[extra] = reqfile.readlines()

    setup(
        name='ncfacbot',
        version='1.0.0',
        author='haliphax',
        packages=['ncfacbot'],
        install_requires=reqs,
        extras_require=extras,
    )
