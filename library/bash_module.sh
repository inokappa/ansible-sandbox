#!/usr/bin/env bash
source $(dirname $0)/args

function create_file() {
  if [ ! -f "/tmp/${file_name}" ];then
    touch /tmp/${file_name}
    if [ $? == "0" ];then
      echo '{"changed": true}'
    else
      echo '{"failed": true}'
    fi
  else
    echo '{"changed": false}'
  fi
}

function delete_file() {
  if [ -f "/tmp/${file_name}" ];then
    rm /tmp/${file_name}
    if [ $? == "0" ];then
      echo '{"changed": true}'
    else
      echo '{"failed": true}'
    fi
  else
    echo '{"changed": false}'
  fi
}

case $state in
  present)
    create_file
    ;;
  absent)
    delete_file
    ;;
  *)
    puts '{"failed": true, "msg": "invalid state: %s"}' "$state"
    exit 1
    ;;
esac
