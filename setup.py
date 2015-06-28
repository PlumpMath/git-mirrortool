from setuptools import setup

setup(name='git-mirrortool',
      version='0.1',
      packages=['git_mirrortool'],
      scripts=['bin/git-mirrortool'],
      install_requires=['requests'],
      author='Ian Denhardt',
      author_email='ian@zenhack.net',
      description='Tool for making mirroring git repos in multiple places easier',
      license='MIT',
      url='https://github.com/zenhack/git-mirrortool',
      )
