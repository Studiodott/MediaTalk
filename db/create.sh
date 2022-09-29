#!/usr/bin/env bash

DIR=`dirname $0`
CREATE="$DIR/create.sql"

[ -e $CREATE ] && psql $DATABASE_URL --file="$CREATE" || echo "no file named $CREATE"
