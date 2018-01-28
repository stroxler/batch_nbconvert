from setuptools import setup

PACKAGE = 'tdx'


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
      keywords='',
      url='https://github.com/stroxler/tdx',
      author='Steven Troxler',
      author_email='steven.troxler@gmail.com',
      license='MIT',
      packages=[PACKAGE],
      install_requires=['plumbum', 'tdx'],
      tests_require=['pytest'],
      include_package_data=True,
      zip_safe=False)
