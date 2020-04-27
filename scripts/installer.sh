#! /usr/bin/env bash
#
set -u
set +e
# set -o noglob
#
workdir=$(cd "$(dirname $0)" && pwd)
topdir=$(cd "${workdir}" && cd .. && pwd)
scriptdir=${workdir}
cd "${workdir}"
#
# lib: color print
bold=$(tput bold)
green=$(tput setf 2)
red=$(tput setf 4)
reset=$(tput sgr0)

function green() {
	  printf "${bold}${green}%s${reset}\n" "$@";
  }
function red() {
	  printf "${bold}${red}%s${reset}\n" "$@";
  }

# green "hello"
# red "hello"

cat << eof
   _____ ______    _____ _                 _   _____           _        _ _           
  / ____|  ____|  / ____| |               | | |_   _|         | |      | | |          
 | |  __| |__    | |    | | ___  _   _  __| |   | |  _ __  ___| |_ __ _| | | ___ _ __ 
 | | |_ |  __|   | |    | |/ _ \| | | |/ _' |   | | | '_ \/ __| __/ _' | | |/ _ \ '__|
 | |__| | |____  | |____| | (_) | |_| | (_| |  _| |_| | | \__ \ || (_| | | |  __/ |   
  \_____|______|  \_____|_|\___/ \__,_|\__,_| |_____|_| |_|___/\__\__,_|_|_|\___|_| 

eof

echo
echo

function install_python3(){
  cd "${scriptdir}"
  if python3 --version &> /dev/null; then
    read -p "$(python3 --version) already installed, proceed anyway(Y/n)? " opt
    if [ "$opt" == "n" ]; then
      return 1
    fi
  fi
  green "yum install python36"
  yum install -y python36
  echo
  sleep 1
  green "$(python3.6 --version)"
}

function install_pip3(){
  green "1. wget https://bootstrap.pypa.io/get-pip.py"
  sleep 1
  wget https://bootstrap.pypa.io/get-pip.py
  green "2. install pip for python3.6"
  python3.6 get-pip.py
  green "$(pip3 --version)"
  echo
}

function install_mariadb(){
  yum install -y mariadb-server-5.5.64
}

function config_mariadb(){
  echo
  # todo
}

function init_db(){
  cd "${scriptdir}"
  read -p "Initialize ge database (Note that this will empty your data, Y/n)?" opt
  if [ 'n' == "$opt" ]; then
    return 1
  fi
  read -p "hostname[localhost]: " hostname
  if [ '' == "$hostname" ]; then hostname='localhost'; fi
  read -p "user[root]: " user
  if [ '' == "$user" ]; then user='root'; fi
  read -p "password[123456]: " password
  if [ "" == "$password" ]; then password='123456'; fi
  sqlfile="dbinit.sql"
  mysql -h${hostname} -u${user} -p${password} < ${sqlfile}
  echo
}

function install_service(){
  cd "${scriptdir}"
  cp gecloud.service /usr/lib/systemd/system
  systemctl daemon-reload
  systemctl enable gecloud.service
  systemctl restart gecloud.service
  systemctl status gecloud.service
  echo
}

function uninstall_service(){
  cd "${scriptdir}"
  systemctl stop gecloud.service
  systemctl disable gecloud.service
  rm -f /usr/lib/systemd/system/gecloud.service
  systemctl daemon-reload
  echo
}


function option1(){
  install_python3
  green "option1 done!"
}
function option2(){
  install_pip3
  green "option2 done!"
}
function option3(){
  install_mariadb
  config_mariadb
  green "option3 done!"
}
function option4(){
  init_db
  green "option4 done!"
}
function option5(){
  install_service
  green "option5 done!"
}
function option6(){
  uninstall_service
  green "option6 done!"
}
function option7(){
  green "option7 done!"
}
function option8(){
  green "option8 done!"
}
function option9(){
  green "option9 done!"
}
function option10(){
  green "option10 done!"
}
function option11(){
  green "option11 done!"
}
function option12(){
  green "option12 done!"
}


cat << eof
====
1) install python3
2) install pip3
3) install and config mariadb
4) init database
5) install service
6) uninstall service
q) quit 
====
eof

while echo; read -p "Enter your option: " option; do
  case $option in
    1)
      option1
      break
      ;;
    2)
      option2
      break
      ;;
    3)
      option3
      break
      ;;
    4)
      option4
      break
      ;;
    5)
      option5
      break
      ;;
    6)
      option6
      break
      ;;
    q|Q)
      break
      ;;
    *)
      echo "invalid option, enter again..."
      continue
  esac
done

