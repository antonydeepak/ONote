from setuptools import setup

from onote.command_line import VERSION


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='onote',
      version=VERSION,
      python_requires='>=3.7',
      description='Search onenote pages',
      long_description=readme(),
      url='https://github.com/antonydeepak/onote',
      author='Antony Thomas',
      author_email='gogsbread@gmail.com',
      packages=['onote'],
      install_requires=[
          'docopt',
          'msal',
          'requests',
      ],
      zip_safe=False,
      entry_points={
          'console_scripts': ['onote=onote.command_line:main'],
      })
