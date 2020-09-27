from setuptools import setup

from onesearch.command_line import VERSION 


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='onesearch',
      version=VERSION,
      python_requires='>=3.7',
      description='Search onenote pages',
      long_description=readme(),
      url='https://github.com/antonydeepak/OneNoteSearch',
      author='Antony Thomas',
      author_email='gogsbread@gmail.com',
      packages=['onesearch'],
      install_requires=[
          'docopt',
          'msal',
          'requests',
      ],
      zip_safe=False,
      entry_points={
          'console_scripts': ['onesearch=onesearch.command_line:main'],
      })
