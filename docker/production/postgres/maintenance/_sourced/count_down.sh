#!/usr/bin/env bash

count_down(){

  declare desc="A simple count down."

  local seconds="${1}"

  local d=$(($(date +%s) + "${seconds}"))

  while [ "$d" -ge `date +%s` ]; do

    echo -ne "$(date -u --date @$(($d - `date +%s`)) +%H:%M:%S)\r";

    sleep 0.1

  done

}