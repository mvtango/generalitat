#! /bin/bash 
cd ~/projekte/generalitat/opengov.cat
rsync -rv ./generalitat/  martin@bitbucket:/home/martin/www.opengov.cat/web/htdocs/embed/generalitat/
