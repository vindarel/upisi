#!/bin/sh

# compléter le pythonpath afin qu'on puisse importer postinstaller dans les tests.
#TODO ne marche pas avec . ni avec source

DIR="$( readlink -e "$( dirname "${0}" )" )"
BASE_DIR="$(readlink -e $DIR/..)"

SRC_DIR="$BASE_DIR"
echo $SRC_DIR
#export PYTHONPATH="$SRC_DIR:$PYTHONPATH"
export PYTHONPATH=$SRC_DIR$PYTHONPATH #mon pythonpath commence déjà par un :
echo $PYTHONPATH