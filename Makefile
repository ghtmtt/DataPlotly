#/***************************************************************************
# DataPlotly
#
# D3 Plots for QGIS
#							 -------------------
#		begin				: 2017-03-05
#		git sha				: $Format:%H$
#		copyright			: (C) 2017 by matteo ghetta
#		email				: matteo.ghetta@gmail.com
# ***************************************************************************/
#
#/***************************************************************************
# *																		 *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or	 *
# *   (at your option) any later version.								   *
# *																		 *
# ***************************************************************************/

#################################################
# Edit the following to match your sources lists
#################################################


PEP8EXCLUDE=pydev,conf.py,third_party,ui,.venv,venv,


#################################################
# Normally you would not need to edit below here
#################################################

test:
	@echo
	@echo "----------------------"
	@echo "Regression Test Suite"
	@echo "----------------------"

	@# Preceding dash means that make will continue in case of errors
	@-export PYTHONPATH=`pwd`:$(PYTHONPATH); \
		export QGIS_DEBUG=0; \
		export QGIS_LOG_FILE=/dev/null; \
		nosetests3 -v -s --with-id --with-coverage --cover-package=. DataPlotly.test \
		3>&1 1>&2 2>&3 3>&- || true
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core error, try sourcing"
	@echo "the helper script we have provided first then run make test."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make test"
	@echo "----------------------"

pylint:
	@echo
	@echo "-----------------"
	@echo "Pylint violations"
	@echo "-----------------"
	@pylint --reports=n --rcfile=pylintrc DataPlotly
	@echo
	@echo "----------------------"
	@echo "If you get a 'no module named qgis.core' error, try sourcing"
	@echo "the helper script we have provided first then run make pylint."
	@echo "e.g. source run-env-linux.sh <path to qgis install>; make pylint"
	@echo "----------------------"


# Run pep8/pycodestyle style checking
#http://pypi.python.org/pypi/pep8
pycodestyle:
	@echo
	@echo "-----------"
	@echo "pycodestyle PEP8 issues"
	@echo "-----------"
	@pycodestyle --repeat --ignore=E203,E121,E122,E123,E124,E125,E126,E127,E128,E402,E501,W504 --exclude $(PEP8EXCLUDE) .
	@echo "-----------"
	@echo "Ignored in PEP8 check:"
	@echo $(PEP8EXCLUDE)
