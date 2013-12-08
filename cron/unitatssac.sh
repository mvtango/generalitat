#! /bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"




cd $DIR/../py
od=../data/xml
of=$od/`date +%Y-%m-%d`-unitatssac.xml

find $od -name '*xml' -mtime +2  -exec gzip {} \;

wget --output-file=/dev/null http://www20.gencat.cat/dadesobertes/recursos/organismes/unitatssac.xml --output-document=$of
python ./maketree.py $of 2>&1 >>../log/maketree.log
python ./organigramas.py $of 2>&1 >>../log/organigramas.log


