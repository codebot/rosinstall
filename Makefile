.PHONY: all setup clean_dist distro clean install testsetup test

NAME='rosinstall'
VERSION=$(shell grep version ./src/rosinstall/__version__.py | sed 's,version = ,,')

OUTPUT_DIR=deb_dist


all:
	echo "noop for debbuild"

setup:
	echo "building version ${VERSION}"

clean_dist:
	-rm -rf src/rosinstall.egg-info
	-rm -rf dist
	-rm -rf deb_dist

distro: setup clean_dist
	python setup.py sdist

clean: clean_dist


install: distro
	sudo checkinstall python setup.py install

testsetup:
	echo "running tests"

test: testsetup
	nosetests --with-coverage --cover-package=rosinstall
