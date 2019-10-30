#!/bin/bash
PLUGINNAME="DataPlotly"
LOCALES=$*
LRELEASE=lrelease

for LOCALE in ${LOCALES}
do
    echo "Processing: ${PLUGINNAME}/i18n/${PLUGINNAME}_${LOCALE}.ts"
    # Note we don't use pylupdate with qt .pro file approach as it is flakey
    # about what is made available.
    ${LRELEASE} ${PLUGINNAME}/i18n/${PLUGINNAME}_${LOCALE}.ts
done
