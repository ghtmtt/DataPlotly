#!/bin/bash
LRELEASE=$1
LOCALES=$*
PLUGINNAME="DataPlotly_"


for LOCALE in ${LOCALES}
do
    echo "Processing: $PLUGINNAME${LOCALE}.ts"
    # Note we don't use pylupdate with qt .pro file approach as it is flakey
    # about what is made available.
    $LRELEASE i18n/$PLUGINNAME${LOCALE}.ts
done
