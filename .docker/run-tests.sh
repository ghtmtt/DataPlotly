#!/bin/bash
#
# Run test in docker QGIS  image
#

set -e

cd  /src

VENV=/src/.docker-venv-$QGIS_VERSION

python3 -m venv $VENV --system-site-package

echo "Installing requirements..."
$VENV/bin/pip install -q --no-cache -r REQUIREMENTS_TESTING.txt

cd tests && $VENV/bin/python -m pytest -v


