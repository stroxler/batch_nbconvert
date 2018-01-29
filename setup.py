from setuptools import setup

PACKAGE = 'batch_nbconvert'


def readme():
    with open('README.md') as f:
        return f.read()


# NOTE: I suspect zip_safe should actually be True, but I haven't
# had time to investigate yet.
setup(name=PACKAGE,
      version="0.0.1",
      description=(
          'Tools for working with container types, command data operations, '
          'and concise exception handling'
      ),
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
      ],
      entry_points={
          "console_scripts": [
              'batch_nbconvert = batch_nbconvert.cli:main',
          ]
      },
      keywords='',
      url='https://github.com/stroxler/batch_nbconvert',
      author='Steven Troxler',
      author_email='steven.troxler@gmail.com',
      license='MIT',
      packages=[PACKAGE],
      install_requires=['plumbum', 'tdx', 'fire',
                        'nbstripout', 'nbconvert'],
      tests_require=['pytest'],
      include_package_data=True,
      zip_safe=False)
