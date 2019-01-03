#!/bin/bash
set -e
export PYTHONPATH=${PWD}:$PYTHONPATH
export DJANGO_SETTINGS_MODULE_ORIG=$DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE="settings-envwrap"
set | grep "DJANGO_"

makemigrations () 
{
    if [ "${DJANGO_AUTOMIGRATE}" == "yes" ]; then
            echo "Perform unapplied migrations..."
            python manage.py migrate || return $?        
    fi;
    return 0
}

dbinit () 
{
    echo "Creating database..."
    python manage.py migrate || return $?
    if [ -n "${DJANGO_DBINIT}" ] && [ -f ${DJANGO_DBINIT} ]; then
        echo "Loading example Database..."
        python manage.py loaddata ${DJANGO_DBINIT} || return $?
    fi;
    return 0
}


check_migrations () 
{
    mstate=(`python manage.py showmigrations -p | awk 'BEGIN {m=0;i=0} /\[ \]/ {m++; if ($3=="auth.0001_initial") i=1;}  END {print "result", i, m}'`)
    [ "${mstate[0]}" == "result" ] || return 255
    
    if [ "${mstate[1]}" == "1" ]; then
        echo "DB not initialized -> dbinit"
        dbinit || return $?
    elif [ "${mstate[2]}" -gt 0 ]; then
        echo "Found ${mstate[2]} not applied migrations."
        makemigrations || return $?
    fi;
    return 0
}

if [ -z "$DJANGO_BACKGROUND" ]; then
    check_migrations || { echo "Check migrations Failed -> exit"; return 255; }
    if [ -n "$DJANGO_CONFIG_STATIC__ROOT" ] && ! [ -f $DJANGO_CONFIG_STATIC__ROOT/.entrypoint.action ]; then
        python manage.py collectstatic -c --noinput
        touch $DJANGO_CONFIG_STATIC__ROOT/.entrypoint.action
    fi;
fi;

echo "exec: $@"
exec "$@"
