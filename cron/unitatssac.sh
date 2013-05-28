#! /bin/bash


DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $DIR
od=../data/xml
of=$od/`date +%Y-%m-%d`-unitatssac.xml
echo $DIR

wget --output-file=/dev/null http://www20.gencat.cat/dadesobertes/recursos/organismes/unitatssac.xml --output-document=$of


