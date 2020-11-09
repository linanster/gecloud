#!/usr/bin/env bash
#
# set -o errexit

# 1.variables definition

usage=$"
Usage:(venv) run.sh  --start [--ssl --nodaemon]
               --stop [--ssl]
               --status
               --init
"
workdir=$(cd "$(dirname $0)" && pwd)

workers=3

# 2.functions definition

function activate_venv() {
    if [ -d venv ]; then
        source ./venv/bin/activate || source ./venv/Script/activate
    else
        echo "==venv error=="
        exit 1
    fi
}

function get_pid(){
    pid=$(ps -ef | fgrep "gunicorn" | grep "application_ge_cloud" | awk '{if($3==1) print $2}')
    echo "$pid"
}


function run_init(){
    pip3 install virtualenv
    virtualenv venv
    source ./venv/bin/activate
    # pip3 install -r requirements.txt
    pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
    if [ $? -eq 0 ]; then
        echo "==init config complete=="
        exit 0
    else
        echo "==init config fail=="
        exit 1
    fi
}


function run_start(){
    activate_venv
    case "$1$2" in
        "")
            cmd="gunicorn --daemon --workers ${workers} --bind 0.0.0.0:5100 --timeout 300 --worker-class eventlet wsgi:application_ge_cloud"
            ;;
        "--nodaemon")
            cmd="gunicorn --workers ${workers} --bind 0.0.0.0:5100 --timeout 300 --worker-class eventlet wsgi:application_ge_cloud"
            ;;
        "--ssl")
            cmd="gunicorn --daemon --workers ${workers} --bind 0.0.0.0:5101 --keyfile ./cert/server.key --certfile ./cert/server.cert --timeout 300 --worker-class eventlet wsgi:application_ge_cloud"
            ;;
        "--ssl--nodaemon"|"--nodaemon--ssl")
            cmd="gunicorn --workers ${workers} --bind 0.0.0.0:5101 --keyfile ./cert/server.key --certfile ./cert/server.cert --timeout 300 --worker-class eventlet wsgi:application_ge_cloud"
            ;;
        *)
            echo "${usage}"
            exit 1
    esac
    echo "${cmd}"
    eval "${cmd}"
    pid=$(get_pid)
    echo "$pid"
    exit 0
}

function run_status(){
    pid=$(ps -ef | fgrep "gunicorn" | grep "application_ge_cloud" | grep 5100 | awk '{if($3==1) print $2}')
    pid_ssl=$(ps -ef | fgrep "gunicorn" | grep "application_ge_cloud" | grep 5101 | awk '{if($3==1) print $2}')
    echo "pid: $pid"
    echo "pid_ssl: $pid_ssl"
    exit 0
}

function run_stop(){
    if [ "$1" == "" ];then
        pid=$(ps -ef | fgrep "gunicorn" | grep "application_ge_cloud" | grep 5100 | awk '{if($3==1) print $2}')
    elif [ "$1" == "--ssl" ]; then
        pid=$(ps -ef | fgrep "gunicorn" | grep "application_ge_cloud" | grep 5101 | awk '{if($3==1) print $2}')
    else
        echo "${usage}"
        exit 1
    fi
    echo "$pid"
    if [ "$pid" == "" ]; then
        echo "not running"
    else
        echo "kill $pid"
        kill "$pid"
    fi
    exit 0

}


# 3.start code

cd "$workdir"

if [ $# -eq 0 ]; then
    echo "${usage}"
    exit 1
fi

if [ $# -ge 1 ]; then
  case $1 in
    --help|-h)
        echo "$usage"
        exit 0
        ;;
    --init)
        run_init
        ;;
    --start)
        run_start $2 $3
        ;;
    --status)
        run_status
        ;;
    --stop)
        run_stop $2
        ;;
    --logmonitor)
        run_logmonitor $2 $3
        ;;
    *)
        echo "$usage"
        exit 1
        ;;
  esac
fi

