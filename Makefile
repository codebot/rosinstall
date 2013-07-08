.PHONY: all setup clean_dist distro clean install deb_dist upload-packages upload-building upload testsetup test

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

push: distro
	python setup.py sdist register upload
	scp dist/rosinstall-${VERSION}.tar.gz root@ipr.willowgarage.com:/var/www/pr.willowgarage.com/html/downloads/rosinstall

clean: clean_dist


install: distro
	sudo checkinstall python setup.py install

deb_dist:
	# need to convert unstable to each distro and repeat
	python setup.py --command-packages=stdeb.command sdist_dsc --workaround-548392=False bdist_deb

upload-packages: deb_dist
	dput -u -c dput.cf all-shadow-fixed ${OUTPUT_DIR}/${NAME}_${VERSION}-1_amd64.changes 
	dput -u -c dput.cf all-ros ${OUTPUT_DIR}/${NAME}_${VERSION}-1_amd64.changes 

upload-building: deb_dist
	dput -u -c dput.cf all-building ${OUTPUT_DIR}/${NAME}_${VERSION}-1_amd64.changes 

upload: upload-building upload-packages

testsetup:
	echo "running tests"

test: testsetup
	nosetests --with-coverage --cover-package=rosinstall
