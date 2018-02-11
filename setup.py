from __future__ import print_function
from setuptools import setup, find_packages
from tfmini import __version__ as VERSION
from build_utils import BuildCommand
from build_utils import PublishCommand
from build_utils import BinaryDistribution

# check rst
# python setup.py check --restructuredtext

PACKAGE_NAME = 'tfmini'
BuildCommand.pkg = PACKAGE_NAME
PublishCommand.pkg = PACKAGE_NAME
PublishCommand.version = VERSION


setup(
	author='Kevin Walchko',
	author_email='walchko@users.noreply.github.com',
	name=PACKAGE_NAME,
	version=VERSION,
	description='A driver for the TFmini LiDAR sold by Sparkfun',
	long_description=open('readme.rst').read(),
	url='http://github.com/walchko/{}'.format(PACKAGE_NAME),
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.6',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Software Development :: Libraries :: Application Frameworks'
	],
	license='MIT',
	keywords=['robot', 'pi', 'serial', 'sensor', 'range', 'ranging', 'robotics', 'tf'],
	packages=find_packages('.'),
	install_requires=['build_utils', 'pyserial'],
	cmdclass={
		'make': BuildCommand,
		'publish': PublishCommand
	}
)
